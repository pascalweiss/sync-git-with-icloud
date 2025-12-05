"""Tests for cloud_operations.py module."""
import os
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from sync_icloud_git.cloud_operations import CloudSyncOperations, ICloudOperations
from sync_icloud_git.config import SyncConfig


class TestCloudOperations:
    """Test cases for CloudSyncOperations class."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        return SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            git_commit_message="Test commit message",
            rclone_config_content="[iclouddrive]\ntype = webdav\nurl = https://p123-caldav.icloud.com\nuser = testuser\npass = testpass",
            rclone_remote_folder="Documents/TestFolder",
            exclude_patterns=[".DS_Store", "*.tmp"],
            step="all"
        )

    @pytest.fixture
    def mock_rclone_config_file(self):
        """Create a mock NamedTemporaryFile for rclone config."""
        mock_file = Mock()
        mock_file.name = "/tmp/test_rclone_config.conf"
        mock_file.write = Mock()
        mock_file.flush = Mock()
        mock_file.close = Mock()
        return mock_file

    @pytest.fixture
    def mock_rclone_module(self):
        """Create a mock rclone module."""
        mock_rclone = Mock()
        mock_rclone.ls.return_value = ["file1.txt", "file2.txt", "subfolder/file3.txt"]
        mock_rclone.sync.return_value = None
        return mock_rclone

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_init_success(self, mock_open_builtin, mock_tempfile, mock_rclone_config_file, capsys):
        """Test successful ICloudOperations initialization."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        # Create a verbose config to see initialization messages
        verbose_config = SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            git_commit_message="Test commit message",
            rclone_config_content="[iclouddrive]\ntype = webdav\nurl = https://p123-caldav.icloud.com\nuser = testuser\npass = testpass",
            rclone_remote_folder="Documents/TestFolder",
            exclude_patterns=[".DS_Store", "*.tmp"],
            step="all",
            verbose=True
        )
        
        icloud_ops = CloudSyncOperations(verbose_config)
        
        # Verify initialization
        assert icloud_ops.config == verbose_config
        assert icloud_ops.git_repo_path == verbose_config.git_repo_path
        assert icloud_ops.rclone_config_content == verbose_config.rclone_config_content
        assert icloud_ops.rclone_remote_folder == verbose_config.rclone_remote_folder
        assert icloud_ops.rclone_config_file == mock_rclone_config_file
        
        # Verify config file setup
        mock_tempfile.assert_called_once_with(mode='w', suffix='.conf', delete=False)
        mock_rclone_config_file.write.assert_called_once_with(verbose_config.rclone_config_content)
        mock_rclone_config_file.flush.assert_called_once()
        mock_rclone_config_file.close.assert_called_once()
        
        # Verify config file verification
        mock_open_builtin.assert_called_with(mock_rclone_config_file.name, 'r', encoding='utf-8')
        
        # Check output messages
        captured = capsys.readouterr()
        assert f"Cloud sync configured: {verbose_config.rclone_remote_name}:{verbose_config.rclone_remote_folder} → test_repo" in captured.out
        assert f"Rclone config ready" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_init_empty_config_file(self, mock_open_builtin, mock_tempfile, sample_config, mock_rclone_config_file):
        """Test initialization with empty config file raises error."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        with pytest.raises(ValueError, match="Rclone config file is empty after write"):
            CloudSyncOperations(sample_config)

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_test_icloud_connection_success(self, mock_rclone, mock_open_builtin, mock_tempfile, 
                                           sample_config, mock_rclone_config_file, capsys):
        """Test successful iCloud connection test."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt", "file2.txt", "folder/file3.txt"]
        
        icloud_ops = CloudSyncOperations(sample_config)
        result = icloud_ops.test_icloud_connection()
        
        assert result == 3
        
        # Verify rclone.ls was called with correct parameters
        expected_remote_path = f"iclouddrive:{sample_config.rclone_remote_folder}"
        mock_rclone.ls.assert_called_once_with(
            expected_remote_path, 
            args=['--config', mock_rclone_config_file.name]
        )
        
        # Check output
        captured = capsys.readouterr()
        assert "Testing cloud storage connection..." in captured.out
        assert "✅ Found 3 items in remote folder" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_test_icloud_connection_failure(self, mock_rclone, mock_open_builtin, mock_tempfile,
                                           sample_config, mock_rclone_config_file, capsys):
        """Test iCloud connection test failure."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.side_effect = RuntimeError("Connection failed")
        
        icloud_ops = CloudSyncOperations(sample_config)
        
        with pytest.raises(RuntimeError, match="Connection failed"):
            icloud_ops.test_icloud_connection()
        
        # Check error output
        captured = capsys.readouterr()
        assert "❌ Failed to connect to remote folder" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_build_remote_path(self, mock_open_builtin, mock_tempfile, sample_config, mock_rclone_config_file):
        """Test remote path building."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        icloud_ops = CloudSyncOperations(sample_config)
        remote_path = icloud_ops._build_remote_path()
        
        expected = f"iclouddrive:{sample_config.rclone_remote_folder}"
        assert remote_path == expected

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.makedirs')
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_sync_from_icloud_to_repo_success(self, mock_rclone, mock_makedirs, mock_open_builtin, 
                                            mock_tempfile, sample_config, mock_rclone_config_file, capsys):
        """Test successful sync from iCloud to repository."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt", "file2.txt"]
        mock_rclone.sync.return_value = None
        
        icloud_ops = CloudSyncOperations(sample_config)
        icloud_ops.sync_from_icloud_to_repo()
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with(sample_config.git_repo_path, exist_ok=True)
        
        # Verify rclone operations
        expected_remote_path = f"iclouddrive:{sample_config.rclone_remote_folder}"
        mock_rclone.ls.assert_called_once()
        mock_rclone.sync.assert_called_once()
        
        # Verify sync call arguments
        sync_call_args = mock_rclone.sync.call_args
        assert sync_call_args[1]['src_path'] == expected_remote_path
        assert sync_call_args[1]['dest_path'] == sample_config.git_repo_path
        assert sync_call_args[1]['show_progress'] is True
        
        # Verify exclude patterns in args
        args = sync_call_args[1]['args']
        assert '--exclude' in args
        assert '.DS_Store' in args
        assert '*.tmp' in args
        
        # Check output
        captured = capsys.readouterr()
        assert "Starting sync from remote folder" in captured.out
        assert "✅ rclone sync completed!" in captured.out
        assert "files in repository" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.makedirs')
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_sync_from_icloud_to_repo_failure(self, mock_rclone, mock_makedirs, mock_open_builtin,
                                             mock_tempfile, sample_config, mock_rclone_config_file, capsys):
        """Test sync failure handling."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt"]
        mock_rclone.sync.side_effect = Exception("Sync failed")
        
        icloud_ops = CloudSyncOperations(sample_config)
        
        with pytest.raises(RuntimeError, match="Sync operation failed: Sync failed"):
            icloud_ops.sync_from_icloud_to_repo()
        
        # Check error output
        captured = capsys.readouterr()
        assert "❌ rclone sync failed: Sync failed" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.makedirs')
    @patch('sync_icloud_git.cloud_operations.rclone')
    @patch.dict('os.environ', {'RCLONE_CONFIG': 'old_config_path'})
    def test_sync_environment_variable_handling(self, mock_rclone, mock_makedirs, mock_open_builtin,
                                               mock_tempfile, sample_config, mock_rclone_config_file):
        """Test proper handling of RCLONE_CONFIG environment variable."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt"]
        mock_rclone.sync.return_value = None
        
        icloud_ops = CloudSyncOperations(sample_config)
        
        # Store original env var value
        original_config = os.environ.get('RCLONE_CONFIG')
        
        icloud_ops.sync_from_icloud_to_repo()
        
        # Verify environment variable was restored
        assert os.environ.get('RCLONE_CONFIG') == original_config

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.makedirs')
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_execute_sync_operation_with_exclude_patterns(self, mock_rclone, mock_makedirs, mock_open_builtin,
                                                         mock_tempfile, sample_config, mock_rclone_config_file, capsys):
        """Test sync operation with exclude patterns."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.sync.return_value = None
        
        icloud_ops = CloudSyncOperations(sample_config)
        remote_path = "iclouddrive:Documents/TestFolder"
        icloud_ops._execute_sync_operation(remote_path)
        
        # Verify sync was called
        sync_call_args = mock_rclone.sync.call_args
        args = sync_call_args[1]['args']
        
        # Check that exclude patterns are properly formatted
        exclude_indices = [i for i, arg in enumerate(args) if arg == '--exclude']
        assert len(exclude_indices) == 2  # Two exclude patterns
        assert args[exclude_indices[0] + 1] == '.DS_Store'
        assert args[exclude_indices[1] + 1] == '*.tmp'
        
        # Check other required arguments
        assert '--config' in args
        assert mock_rclone_config_file.name in args
        assert '--transfers' in args
        assert '3' in args
        assert '--checkers' in args
        assert '4' in args
        
        # Check output
        captured = capsys.readouterr()
        assert "Excluding 2 patterns: .DS_Store, *.tmp" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.makedirs')
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_execute_sync_operation_no_exclude_patterns(self, mock_rclone, mock_makedirs, mock_open_builtin,
                                                       mock_tempfile, mock_rclone_config_file):
        """Test sync operation with only default exclude patterns."""
        # Create config without additional exclude patterns (still gets defaults)
        config = SyncConfig(
            git_repo_path="/tmp/test_repo",
            rclone_config_content="test config",
            rclone_remote_folder="Documents/TestFolder"
        )
        
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.sync.return_value = None
        
        icloud_ops = CloudSyncOperations(config)
        remote_path = "iclouddrive:Documents/TestFolder"
        icloud_ops._execute_sync_operation(remote_path)
        
        # Verify sync was called with default exclude patterns only
        sync_call_args = mock_rclone.sync.call_args
        args = sync_call_args[1]['args']
        
        # Should contain default --exclude arguments for git files
        assert '--exclude' in args
        # Verify some default excludes are present
        exclude_args = [args[i+1] for i, arg in enumerate(args) if arg == '--exclude']
        assert "'.git/'" in exclude_args
        assert "'.gitmodules'" in exclude_args

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.walk')
    @patch('sync_icloud_git.cloud_operations.os.path.exists')
    def test_count_synced_files(self, mock_exists, mock_walk, mock_open_builtin, mock_tempfile,
                               sample_config, mock_rclone_config_file):
        """Test counting synced files."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_exists.return_value = True
        mock_walk.return_value = [
            ('/tmp/test_repo', ['subfolder'], ['file1.txt', 'file2.txt']),
            ('/tmp/test_repo/subfolder', [], ['file3.txt']),
            ('/tmp/test_repo/.git', [], ['config'])  # Should be skipped
        ]
        
        icloud_ops = CloudSyncOperations(sample_config)
        synced_files = icloud_ops._count_synced_files()
        
        expected_files = [
            '/tmp/test_repo/file1.txt',
            '/tmp/test_repo/file2.txt',
            '/tmp/test_repo/subfolder/file3.txt'
        ]
        assert synced_files == expected_files

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.path.exists')
    def test_count_synced_files_no_directory(self, mock_exists, mock_open_builtin, mock_tempfile,
                                           sample_config, mock_rclone_config_file):
        """Test counting synced files when directory doesn't exist."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_exists.return_value = False
        
        icloud_ops = CloudSyncOperations(sample_config)
        synced_files = icloud_ops._count_synced_files()
        
        assert synced_files == []

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_log_sync_parameters(self, mock_open_builtin, mock_tempfile, sample_config, 
                                mock_rclone_config_file, capsys):
        """Test logging of sync parameters."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        icloud_ops = CloudSyncOperations(sample_config)
        remote_path = "iclouddrive:Documents/TestFolder"
        args = ['--config', '/tmp/config', '--transfers', '3']
        
        icloud_ops._log_sync_parameters(remote_path, args)
        
        # Check debug output
        captured = capsys.readouterr()
        assert "Syncing from" in captured.out
        assert remote_path in captured.out
        assert sample_config.git_repo_path in captured.out
        assert f"Excluding {len(sample_config.exclude_patterns)} patterns:" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_execute_sync_with_library(self, mock_rclone, mock_open_builtin, mock_tempfile,
                                     sample_config, mock_rclone_config_file, capsys):
        """Test direct execution with rclone library."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.sync.return_value = None
        
        icloud_ops = CloudSyncOperations(sample_config)
        remote_path = "iclouddrive:Documents/TestFolder"
        args = ['--config', '/tmp/config']
        
        icloud_ops._execute_sync_with_library(remote_path, args)
        
        # Verify rclone.sync was called with correct parameters
        mock_rclone.sync.assert_called_once_with(
            src_path=remote_path,
            dest_path=sample_config.git_repo_path,
            args=args,
            show_progress=True
        )
        
        # Check output
        captured = capsys.readouterr()
        assert "✅ rclone sync completed!" in captured.out
        assert "files in repository" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.path.exists')
    @patch('sync_icloud_git.cloud_operations.os.unlink')
    def test_cleanup_rclone_config(self, mock_unlink, mock_exists, mock_open_builtin, mock_tempfile,
                                  mock_rclone_config_file, capsys):
        """Test cleanup of rclone config file."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_exists.return_value = True
        
        # Create a verbose config to see cleanup messages
        verbose_config = SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            git_commit_message="Test commit message",
            rclone_config_content="[iclouddrive]\ntype = webdav\nurl = https://p123-caldav.icloud.com\nuser = testuser\npass = testpass",
            rclone_remote_folder="Documents/TestFolder",
            exclude_patterns=[".DS_Store", "*.tmp"],
            step="all",
            verbose=True
        )
        
        icloud_ops = CloudSyncOperations(verbose_config)
        icloud_ops._cleanup_rclone_config()
        
        # Verify cleanup operations
        mock_exists.assert_called_once_with(mock_rclone_config_file.name)
        mock_unlink.assert_called_once_with(mock_rclone_config_file.name)
        
        # Check output
        captured = capsys.readouterr()
        assert "Cleaned up rclone config file" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.os.path.exists')
    def test_cleanup_rclone_config_file_not_exists(self, mock_exists, mock_open_builtin, mock_tempfile,
                                                  sample_config, mock_rclone_config_file):
        """Test cleanup when config file doesn't exist."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_exists.return_value = False
        
        icloud_ops = CloudSyncOperations(sample_config)
        # Reset the call count after initialization
        mock_exists.reset_mock()
        
        icloud_ops._cleanup_rclone_config()
        
        # Should not attempt to unlink
        mock_exists.assert_called_once_with(mock_rclone_config_file.name)

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_repr(self, mock_open_builtin, mock_tempfile, sample_config, mock_rclone_config_file):
        """Test string representation of ICloudOperations."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        icloud_ops = CloudSyncOperations(sample_config)
        repr_str = repr(icloud_ops)

        expected = f"CloudSyncOperations(git_repo_path='{sample_config.git_repo_path}', rclone_remote_name='{sample_config.rclone_remote_name}', rclone_remote_folder='{sample_config.rclone_remote_folder}')"
        assert repr_str == expected

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_del_cleanup(self, mock_open_builtin, mock_tempfile, sample_config, mock_rclone_config_file):
        """Test cleanup during object destruction."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        with patch.object(ICloudOperations, '_cleanup_rclone_config') as mock_cleanup:
            icloud_ops = CloudSyncOperations(sample_config)
            del icloud_ops
            mock_cleanup.assert_called_once()

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_del_cleanup_error(self, mock_open_builtin, mock_tempfile, sample_config, mock_rclone_config_file):
        """Test cleanup error handling during object destruction."""
        mock_tempfile.return_value = mock_rclone_config_file
        
        with patch.object(ICloudOperations, '_cleanup_rclone_config', side_effect=OSError("Cleanup failed")):
            icloud_ops = CloudSyncOperations(sample_config)
            # Should not raise exception during deletion
            del icloud_ops

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_edge_case_empty_remote_folder(self, mock_rclone, mock_open_builtin, mock_tempfile, mock_rclone_config_file):
        """Test behavior with empty remote folder."""
        config = SyncConfig(
            git_repo_path="/tmp/test_repo",
            rclone_config_content="test config",
            rclone_remote_folder=""
        )
        
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = []
        
        icloud_ops = CloudSyncOperations(config)
        remote_path = icloud_ops._build_remote_path()
        
        assert remote_path == "iclouddrive:"

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_edge_case_special_characters_in_folder(self, mock_rclone, mock_open_builtin, mock_tempfile, mock_rclone_config_file):
        """Test behavior with special characters in folder name."""
        config = SyncConfig(
            git_repo_path="/tmp/test_repo",
            rclone_config_content="test config",
            rclone_remote_folder="Documents/Test Folder (2023) & More!"
        )
        
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt"]
        
        icloud_ops = CloudSyncOperations(config)
        remote_path = icloud_ops._build_remote_path()
        
        assert remote_path == "iclouddrive:Documents/Test Folder (2023) & More!"

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_integration_full_sync_workflow(self, mock_rclone, mock_open_builtin, mock_tempfile,
                                          sample_config, mock_rclone_config_file, capsys):
        """Test complete sync workflow integration."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt", "file2.txt", "folder/file3.txt"]
        mock_rclone.sync.return_value = None
        
        with patch('sync_icloud_git.cloud_operations.os.makedirs') as mock_makedirs:
            icloud_ops = CloudSyncOperations(sample_config)
            
            # Test connection first
            file_count = icloud_ops.test_icloud_connection()
            assert file_count == 3
            
            # Test full sync
            icloud_ops.sync_from_icloud_to_repo()
            
            # Verify all operations
            mock_makedirs.assert_called_with(sample_config.git_repo_path, exist_ok=True)
            assert mock_rclone.ls.call_count == 2  # Once for test, once for sync
            mock_rclone.sync.assert_called_once()
            
            # Check final output
            captured = capsys.readouterr()
            assert "✅ Found 3 items in remote folder" in captured.out
            assert "✅ rclone sync completed!" in captured.out

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_configurable_remote_name_nextcloud(self, mock_open_builtin, mock_tempfile, mock_rclone_config_file):
        """Test CloudSyncOperations with Nextcloud remote name."""
        mock_tempfile.return_value = mock_rclone_config_file

        nextcloud_config = SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            rclone_config_content="[nextcloud]\ntype = webdav\nurl = https://cloud.example.com\nvendor = nextcloud",
            rclone_remote_folder="Documents/TestFolder",
            rclone_remote_name="nextcloud",
            step="all"
        )

        cloud_ops = CloudSyncOperations(nextcloud_config)
        remote_path = cloud_ops._build_remote_path()

        assert cloud_ops.rclone_remote_name == "nextcloud"
        assert remote_path == "nextcloud:Documents/TestFolder"

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_configurable_remote_name_gdrive(self, mock_open_builtin, mock_tempfile, mock_rclone_config_file):
        """Test CloudSyncOperations with Google Drive remote name."""
        mock_tempfile.return_value = mock_rclone_config_file

        gdrive_config = SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            rclone_config_content="[gdrive]\ntype = drive\nclient_id = xxx",
            rclone_remote_folder="MyFolder",
            rclone_remote_name="gdrive",
            step="all"
        )

        cloud_ops = CloudSyncOperations(gdrive_config)
        remote_path = cloud_ops._build_remote_path()

        assert cloud_ops.rclone_remote_name == "gdrive"
        assert remote_path == "gdrive:MyFolder"

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    def test_default_remote_name_backward_compatibility(self, mock_open_builtin, mock_tempfile, mock_rclone_config_file):
        """Test that default remote name is 'iclouddrive' for backward compatibility."""
        mock_tempfile.return_value = mock_rclone_config_file

        # Config without explicit remote name should default to 'iclouddrive'
        config_without_remote_name = SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            rclone_config_content="[iclouddrive]\ntype = webdav",
            rclone_remote_folder="Documents/TestFolder",
            step="all"
        )

        cloud_ops = CloudSyncOperations(config_without_remote_name)
        remote_path = cloud_ops._build_remote_path()

        assert cloud_ops.rclone_remote_name == "iclouddrive"
        assert remote_path == "iclouddrive:Documents/TestFolder"

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_backward_compatibility_alias_icloud_operations(self, mock_rclone, mock_open_builtin, mock_tempfile,
                                                           sample_config, mock_rclone_config_file):
        """Test that ICloudOperations alias works for backward compatibility."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt"]

        # ICloudOperations should be an alias to CloudSyncOperations
        ops = ICloudOperations(sample_config)

        assert isinstance(ops, CloudSyncOperations)
        assert ops.__class__.__name__ == "CloudSyncOperations"

    @patch('sync_icloud_git.cloud_operations.tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open, read_data="config content")
    @patch('sync_icloud_git.cloud_operations.rclone')
    def test_backward_compatibility_method_aliases(self, mock_rclone, mock_open_builtin, mock_tempfile,
                                                   sample_config, mock_rclone_config_file):
        """Test that deprecated method names work for backward compatibility."""
        mock_tempfile.return_value = mock_rclone_config_file
        mock_rclone.ls.return_value = ["file1.txt"]
        mock_rclone.sync.return_value = None

        ops = CloudSyncOperations(sample_config)

        # Test deprecated method test_icloud_connection()
        with patch('sync_icloud_git.cloud_operations.os.makedirs'):
            file_count = ops.test_icloud_connection()
            assert file_count == 1

        # Test deprecated method sync_from_icloud_to_repo()
        with patch('sync_icloud_git.cloud_operations.os.makedirs'):
            ops.sync_from_icloud_to_repo()
            mock_rclone.sync.assert_called_once()
