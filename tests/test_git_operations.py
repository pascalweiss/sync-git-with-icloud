"""Tests for git_operations.py module."""
import os
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
import git.exc
from sync_icloud_git.git_operations import GitOperations
from sync_icloud_git.config import SyncConfig


class TestGitOperations:
    """Test cases for GitOperations class."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        return SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="testuser",
            git_pat="test_token",
            git_repo_path="/tmp/test_repo",
            git_commit_message="Test commit message",
            rclone_config_content="test_config",
            rclone_remote_folder="test_folder",
            step="all"
        )

    @pytest.fixture
    def mock_repo(self):
        """Create a mock Git repository object."""
        mock_repo = Mock()
        mock_repo.is_dirty.return_value = False
        mock_repo.submodules = []
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mock_repo.remotes.origin = Mock()
        mock_repo.remotes.origin.fetch.return_value = None
        mock_repo.remotes.origin.pull.return_value = None
        mock_repo.remotes.origin.set_url.return_value = None
        mock_repo.remotes.origin.push.return_value = None
        mock_repo.git = Mock()
        mock_repo.index = Mock()
        mock_repo.iter_commits.return_value = []
        mock_repo.remote.return_value = mock_repo.remotes.origin
        return mock_repo

    @pytest.fixture
    def mock_submodule(self):
        """Create a mock submodule object."""
        mock_submodule = Mock()
        mock_submodule.name = "test_submodule"
        mock_submodule.url = "https://github.com/test/submodule.git"
        
        # Mock the submodule repository
        mock_submodule_repo = Mock()
        mock_submodule_repo.is_dirty.return_value = False
        mock_submodule_repo.git = Mock()
        mock_submodule_repo.index = Mock()
        mock_submodule_repo.iter_commits.return_value = []
        mock_submodule_repo.remote.return_value = Mock()
        mock_submodule.module.return_value = mock_submodule_repo
        
        return mock_submodule

    def test_init_without_credentials(self, sample_config):
        """Test GitOperations initialization without credentials."""
        config = SyncConfig(git_repo_path="/tmp/test")
        git_ops = GitOperations(config)
        
        assert git_ops.config == config
        assert git_ops.git_remote_url is None
        assert git_ops.git_username is None
        assert git_ops.git_pat is None
        assert git_ops.git_repo_path == "/tmp/test"
        assert git_ops.repo is None

    def test_init_with_credentials(self, sample_config, capsys):
        """Test GitOperations initialization with credentials."""
        git_ops = GitOperations(sample_config)
        
        assert git_ops.config == sample_config
        assert git_ops.git_remote_url == sample_config.git_remote_url
        assert git_ops.git_username == sample_config.git_username
        assert git_ops.git_pat == sample_config.git_pat
        assert git_ops.git_repo_path == sample_config.git_repo_path
        assert git_ops.repo is None
        
        # Check that authentication message was printed
        captured = capsys.readouterr()
        assert "Git authentication configured for user: testuser" in captured.out

    def test_get_auth_url_with_https(self, sample_config):
        """Test URL authentication credential embedding with HTTPS."""
        git_ops = GitOperations(sample_config)
        
        # Test with default URL
        auth_url = git_ops._get_auth_url()
        expected = "https://testuser:test_token@github.com/test/repo.git"
        assert auth_url == expected
        
        # Test with custom URL
        custom_url = "https://gitlab.com/user/project.git"
        auth_url = git_ops._get_auth_url(custom_url)
        expected = "https://testuser:test_token@gitlab.com/user/project.git"
        assert auth_url == expected

    def test_get_auth_url_with_ssh(self, sample_config):
        """Test URL authentication with SSH URL (should return as-is)."""
        git_ops = GitOperations(sample_config)
        
        ssh_url = "git@github.com:test/repo.git"
        auth_url = git_ops._get_auth_url(ssh_url)
        assert auth_url == ssh_url

    def test_get_auth_url_without_credentials(self):
        """Test URL authentication without credentials."""
        config = SyncConfig(git_remote_url="https://github.com/test/repo.git")
        git_ops = GitOperations(config)
        
        auth_url = git_ops._get_auth_url()
        assert auth_url == "https://github.com/test/repo.git"

    def test_get_auth_url_with_http(self, sample_config):
        """Test URL authentication with HTTP (non-HTTPS) URL."""
        git_ops = GitOperations(sample_config)
        
        http_url = "http://example.com/repo.git"
        auth_url = git_ops._get_auth_url(http_url)
        assert auth_url == http_url  # Should return as-is for non-HTTPS

    @patch('sync_icloud_git.git_operations.os.path.exists')
    def test_check_and_update_repo_not_exists(self, mock_exists, sample_config):
        """Test check_and_update_repo when repository doesn't exist."""
        mock_exists.return_value = False
        
        git_ops = GitOperations(sample_config)
        result = git_ops.check_and_update_repo()
        
        assert result is False
        mock_exists.assert_called()

    @patch('sync_icloud_git.git_operations.os.path.exists')
    def test_check_and_update_repo_git_folder_missing(self, mock_exists, sample_config):
        """Test check_and_update_repo when .git folder is missing."""
        # First call (repo path) returns True, second call (.git path) returns False
        mock_exists.side_effect = [True, False]
        
        git_ops = GitOperations(sample_config)
        result = git_ops.check_and_update_repo()
        
        assert result is False
        assert mock_exists.call_count == 2

    @patch('sync_icloud_git.git_operations.git.Repo')
    @patch('sync_icloud_git.git_operations.os.path.exists')
    def test_check_and_update_repo_success(self, mock_exists, mock_repo_class, sample_config, mock_repo, capsys):
        """Test successful repository update."""
        mock_exists.return_value = True
        mock_repo_class.return_value = mock_repo
        
        git_ops = GitOperations(sample_config)
        result = git_ops.check_and_update_repo()
        
        assert result is True
        assert git_ops.repo == mock_repo
        
        # Verify the sequence of operations
        mock_repo_class.assert_called_once_with(sample_config.git_repo_path)
        mock_repo.remotes.origin.set_url.assert_called_once()
        mock_repo.remotes.origin.fetch.assert_called_once()
        mock_repo.remotes.origin.pull.assert_called_once_with("main")
        
        # Check output messages
        captured = capsys.readouterr()
        assert "Found existing git repository" in captured.out
        assert "Fetching and pulling latest changes" in captured.out
        assert "Repository and submodules updated successfully" in captured.out

    @patch('sync_icloud_git.git_operations.git.Repo')
    @patch('sync_icloud_git.git_operations.os.path.exists')
    def test_check_and_update_repo_detached_head(self, mock_exists, mock_repo_class, sample_config, mock_repo):
        """Test repository update with detached HEAD."""
        mock_exists.return_value = True
        mock_repo.head.is_detached = True
        mock_repo_class.return_value = mock_repo
        
        git_ops = GitOperations(sample_config)
        result = git_ops.check_and_update_repo()
        
        assert result is True
        # Should try to checkout main branch first
        mock_repo.git.checkout.assert_called_with('main')

    @patch('sync_icloud_git.git_operations.git.Repo')
    @patch('sync_icloud_git.git_operations.os.path.exists')
    def test_check_and_update_repo_detached_head_fallback_to_master(self, mock_exists, mock_repo_class, sample_config, mock_repo):
        """Test repository update with detached HEAD, fallback to master."""
        mock_exists.return_value = True
        mock_repo.head.is_detached = True
        mock_repo_class.return_value = mock_repo
        
        # Make checkout('main') fail, but checkout('master') succeed
        mock_repo.git.checkout.side_effect = [git.exc.GitCommandError("checkout", "failed"), None]
        
        git_ops = GitOperations(sample_config)
        result = git_ops.check_and_update_repo()
        
        assert result is True
        # Should try both main and master
        expected_calls = [call('main'), call('master')]
        mock_repo.git.checkout.assert_has_calls(expected_calls)

    @patch('sync_icloud_git.git_operations.git.Repo')
    @patch('sync_icloud_git.git_operations.os.path.exists')
    def test_check_and_update_repo_exception(self, mock_exists, mock_repo_class, sample_config):
        """Test repository update with exception."""
        mock_exists.return_value = True
        mock_repo_class.side_effect = Exception("Git error")
        
        git_ops = GitOperations(sample_config)
        
        with pytest.raises(Exception, match="Git error"):
            git_ops.check_and_update_repo()

    @patch('sync_icloud_git.git_operations.git.Repo.clone_from')
    @patch('sync_icloud_git.git_operations.os.makedirs')
    def test_clone_repo_success(self, mock_makedirs, mock_clone, sample_config, mock_repo, capsys):
        """Test successful repository cloning."""
        mock_clone.return_value = mock_repo
        
        git_ops = GitOperations(sample_config)
        result = git_ops.clone_repo()
        
        assert result is True
        assert git_ops.repo == mock_repo
        
        # Verify operations
        mock_makedirs.assert_called_once_with(os.path.dirname(sample_config.git_repo_path), exist_ok=True)
        mock_clone.assert_called_once_with(
            "https://testuser:test_token@github.com/test/repo.git",
            sample_config.git_repo_path,
            recursive=False
        )
        
        # Check output
        captured = capsys.readouterr()
        assert "Cloning repository from" in captured.out
        assert "Repository cloned successfully" in captured.out

    @patch('sync_icloud_git.git_operations.git.Repo.clone_from')
    @patch('sync_icloud_git.git_operations.os.makedirs')
    def test_clone_repo_failure(self, mock_makedirs, mock_clone, sample_config, capsys):
        """Test repository cloning failure."""
        mock_clone.side_effect = Exception("Clone failed")
        
        git_ops = GitOperations(sample_config)
        result = git_ops.clone_repo()
        
        assert result is False
        assert git_ops.repo is None
        
        # Check error output
        captured = capsys.readouterr()
        assert "Error cloning repository: Clone failed" in captured.out

    def test_setup_submodules_no_submodules(self, sample_config, mock_repo):
        """Test _setup_submodules when no submodules exist."""
        mock_repo.submodules = []
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        # Should not raise an exception and return early
        git_ops._setup_submodules()
        
        # No git operations should be called
        mock_repo.git.config.assert_not_called()
        mock_repo.git.submodule.assert_not_called()

    def test_setup_submodules_with_submodules(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test _setup_submodules with submodules."""
        mock_repo.submodules = [mock_submodule]
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        git_ops._setup_submodules()
        
        # Verify submodule configuration
        mock_repo.git.config.assert_called_once_with(
            f'submodule.{mock_submodule.name}.url',
            'https://testuser:test_token@github.com/test/submodule.git'
        )
        mock_repo.git.submodule.assert_called_once_with('update', '--init', '--remote', '--recursive')
        
        # Verify branch checkout attempt
        mock_submodule.module().git.checkout.assert_called_with('main')
        
        # Check output
        captured = capsys.readouterr()
        assert "Found 1 submodules, updating to latest" in captured.out
        assert "Updated submodule 'test_submodule' on 'main'" in captured.out

    def test_setup_submodules_checkout_fallback_to_master(self, sample_config, mock_repo, mock_submodule):
        """Test _setup_submodules with checkout fallback to master."""
        mock_repo.submodules = [mock_submodule]
        mock_submodule.url = "git@github.com:test/submodule.git"  # SSH URL, no auth config
        
        # Make checkout('main') fail, but checkout('master') succeed
        mock_submodule.module().git.checkout.side_effect = [Exception("main failed"), None]
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        git_ops._setup_submodules()
        
        # Should not configure auth for SSH URL
        mock_repo.git.config.assert_not_called()
        
        # Should try both main and master
        expected_calls = [call('main'), call('master')]
        mock_submodule.module().git.checkout.assert_has_calls(expected_calls)

    def test_commit_changes_no_repo(self, sample_config, capsys):
        """Test commit_changes when no repository is loaded."""
        git_ops = GitOperations(sample_config)
        git_ops.repo = None
        
        result = git_ops.commit_changes()
        
        assert result is False
        captured = capsys.readouterr()
        assert "No repository loaded. Cannot commit changes." in captured.out

    def test_commit_changes_no_changes(self, sample_config, mock_repo, capsys):
        """Test commit_changes when there are no changes."""
        mock_repo.is_dirty.return_value = False
        mock_repo.submodules = []
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.commit_changes()
        
        assert result is False
        captured = capsys.readouterr()
        assert "No changes to commit in main repository" in captured.out
        assert "No changes found to commit in any repository" in captured.out

    def test_commit_changes_main_repo_only(self, sample_config, mock_repo, capsys):
        """Test commit_changes with changes in main repository only."""
        mock_repo.is_dirty.return_value = True
        mock_repo.submodules = []
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.commit_changes()
        
        assert result is True
        
        # Verify git operations
        mock_repo.git.add.assert_called_once_with('-A')
        mock_repo.index.commit.assert_called_once_with(sample_config.git_commit_message)
        
        # Check output
        captured = capsys.readouterr()
        assert "Committing changes in main repository" in captured.out
        assert "Successfully committed changes in main repository" in captured.out
        assert "Changes committed successfully in: main repository" in captured.out
        assert f"Commit message used: '{sample_config.git_commit_message}'" in captured.out

    def test_commit_changes_submodule_only(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test commit_changes with changes in submodule only."""
        mock_repo.is_dirty.return_value = False
        mock_repo.submodules = [mock_submodule]
        mock_submodule.module().is_dirty.return_value = True
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.commit_changes()
        
        assert result is True
        
        # Verify submodule operations
        mock_submodule.module().git.add.assert_called_once_with('-A')
        mock_submodule.module().index.commit.assert_called_once_with(sample_config.git_commit_message)
        
        # Main repo should not be committed
        mock_repo.git.add.assert_not_called()
        
        # Check output
        captured = capsys.readouterr()
        assert "Committing changes in submodule: test_submodule" in captured.out
        assert "Successfully committed changes in submodule: test_submodule" in captured.out
        assert "No changes to commit in main repository" in captured.out
        assert "Changes committed successfully in: submodule 'test_submodule'" in captured.out

    def test_commit_changes_both_main_and_submodule(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test commit_changes with changes in both main repo and submodule."""
        mock_repo.is_dirty.return_value = True
        mock_repo.submodules = [mock_submodule]
        mock_submodule.module().is_dirty.return_value = True
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.commit_changes()
        
        assert result is True
        
        # Verify both operations
        mock_submodule.module().git.add.assert_called_once_with('-A')
        mock_submodule.module().index.commit.assert_called_once_with(sample_config.git_commit_message)
        mock_repo.git.add.assert_called_once_with('-A')
        mock_repo.index.commit.assert_called_once_with(sample_config.git_commit_message)
        
        # Check output
        captured = capsys.readouterr()
        assert "Changes committed successfully in: submodule 'test_submodule', main repository" in captured.out

    def test_commit_changes_submodule_error(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test commit_changes with submodule error (should continue)."""
        mock_repo.is_dirty.return_value = True
        mock_repo.submodules = [mock_submodule]
        mock_submodule.module().is_dirty.return_value = True
        mock_submodule.module().git.add.side_effect = Exception("Submodule error")
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.commit_changes()
        
        assert result is True  # Should still succeed with main repo
        
        # Main repo should still be committed
        mock_repo.git.add.assert_called_once_with('-A')
        mock_repo.index.commit.assert_called_once_with(sample_config.git_commit_message)
        
        # Check error output
        captured = capsys.readouterr()
        assert "Error committing changes in submodule test_submodule: Submodule error" in captured.out
        assert "Changes committed successfully in: main repository" in captured.out

    def test_commit_changes_exception(self, sample_config, mock_repo, capsys):
        """Test commit_changes with general exception."""
        mock_repo.is_dirty.side_effect = Exception("General error")
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.commit_changes()
        
        assert result is False
        captured = capsys.readouterr()
        assert "Error committing changes: General error" in captured.out

    def test_push_changes_no_repo(self, sample_config, capsys):
        """Test push_changes when no repository is loaded."""
        git_ops = GitOperations(sample_config)
        git_ops.repo = None
        
        result = git_ops.push_changes()
        
        assert result is False
        captured = capsys.readouterr()
        assert "No repository loaded. Cannot push changes." in captured.out

    def test_push_changes_no_commits(self, sample_config, mock_repo, capsys):
        """Test push_changes when there are no commits to push."""
        mock_repo.iter_commits.return_value = []
        mock_repo.submodules = []
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.push_changes()
        
        assert result is False
        captured = capsys.readouterr()
        assert "No commits to push in main repository" in captured.out
        assert "No changes found to push in any repository" in captured.out

    def test_push_changes_main_repo_only(self, sample_config, mock_repo, capsys):
        """Test push_changes with commits in main repository only."""
        # Mock commits to push
        mock_commits = [Mock(), Mock()]
        mock_repo.iter_commits.return_value = mock_commits
        mock_repo.submodules = []
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.push_changes()
        
        assert result is True
        
        # Verify push operation
        mock_repo.remote.assert_called_once_with('origin')
        mock_repo.remotes.origin.push.assert_called_once()
        
        # Check output
        captured = capsys.readouterr()
        assert "Pushing changes in main repository" in captured.out
        assert "Successfully pushed changes in main repository" in captured.out
        assert "Changes pushed successfully to: main repository" in captured.out

    def test_push_changes_submodule_only(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test push_changes with commits in submodule only."""
        mock_repo.iter_commits.return_value = []
        mock_repo.submodules = [mock_submodule]
        
        # Mock submodule has commits to push
        mock_commits = [Mock(), Mock()]
        mock_submodule.module().iter_commits.return_value = mock_commits
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.push_changes()
        
        assert result is True
        
        # Verify submodule push
        mock_submodule.module().remote.assert_called_once_with('origin')
        mock_submodule.module().remote().push.assert_called_once()
        
        # Check output
        captured = capsys.readouterr()
        assert "Pushing changes in submodule: test_submodule" in captured.out
        assert "Successfully pushed changes in submodule: test_submodule" in captured.out
        assert "No commits to push in main repository" in captured.out
        assert "Changes pushed successfully to: submodule 'test_submodule'" in captured.out

    def test_push_changes_both_main_and_submodule(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test push_changes with commits in both main repo and submodule."""
        # Both have commits to push
        mock_commits = [Mock(), Mock()]
        mock_repo.iter_commits.return_value = mock_commits
        mock_repo.submodules = [mock_submodule]
        mock_submodule.module().iter_commits.return_value = mock_commits
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.push_changes()
        
        assert result is True
        
        # Verify both push operations
        mock_submodule.module().remote.assert_called_once_with('origin')
        mock_submodule.module().remote().push.assert_called_once()
        mock_repo.remote.assert_called_once_with('origin')
        mock_repo.remotes.origin.push.assert_called_once()
        
        # Check output
        captured = capsys.readouterr()
        assert "Changes pushed successfully to: submodule 'test_submodule', main repository" in captured.out

    def test_push_changes_submodule_error(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test push_changes with submodule error (should continue)."""
        mock_commits = [Mock(), Mock()]
        mock_repo.iter_commits.return_value = mock_commits
        mock_repo.submodules = [mock_submodule]
        mock_submodule.module().iter_commits.return_value = mock_commits
        mock_submodule.module().remote.side_effect = Exception("Push error")
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.push_changes()
        
        assert result is True  # Should still succeed with main repo
        
        # Main repo should still be pushed
        mock_repo.remote.assert_called_once_with('origin')
        mock_repo.remotes.origin.push.assert_called_once()
        
        # Check error output
        captured = capsys.readouterr()
        assert "Error pushing changes in submodule test_submodule: Push error" in captured.out
        assert "Changes pushed successfully to: main repository" in captured.out

    def test_push_changes_exception(self, sample_config, mock_repo, capsys):
        """Test push_changes with general exception."""
        mock_repo.iter_commits.side_effect = Exception("General error")
        
        git_ops = GitOperations(sample_config)
        git_ops.repo = mock_repo
        
        result = git_ops.push_changes()
        
        assert result is False
        captured = capsys.readouterr()
        assert "Error pushing changes: General error" in captured.out

    def test_repr(self, sample_config):
        """Test string representation of GitOperations."""
        git_ops = GitOperations(sample_config)
        repr_str = repr(git_ops)
        
        expected = f"GitOperations(git_repo_path='{sample_config.git_repo_path}')"
        assert repr_str == expected

    def test_integration_clone_commit_push_workflow(self, sample_config, mock_repo, mock_submodule, capsys):
        """Test integration of clone -> commit -> push workflow."""
        with patch('sync_icloud_git.git_operations.git.Repo.clone_from') as mock_clone, \
             patch('sync_icloud_git.git_operations.os.makedirs') as mock_makedirs:
            
            # Setup mocks for workflow
            mock_clone.return_value = mock_repo
            mock_repo.is_dirty.return_value = True
            mock_repo.submodules = [mock_submodule]
            mock_submodule.module().is_dirty.return_value = True
            mock_commits = [Mock()]
            mock_repo.iter_commits.return_value = mock_commits
            mock_submodule.module().iter_commits.return_value = mock_commits
            
            git_ops = GitOperations(sample_config)
            
            # 1. Clone
            clone_result = git_ops.clone_repo()
            assert clone_result is True
            assert git_ops.repo == mock_repo
            
            # 2. Commit
            commit_result = git_ops.commit_changes()
            assert commit_result is True
            
            # 3. Push
            push_result = git_ops.push_changes()
            assert push_result is True
            
            # Verify all operations were called
            mock_clone.assert_called_once()
            mock_repo.git.add.assert_called_once_with('-A')
            mock_repo.index.commit.assert_called_once()
            mock_submodule.module().git.add.assert_called_once_with('-A')
            mock_submodule.module().index.commit.assert_called_once()
            mock_repo.remotes.origin.push.assert_called_once()
            mock_submodule.module().remote().push.assert_called_once()

    def test_edge_case_empty_commit_message(self):
        """Test behavior with empty commit message (should use default)."""
        config = SyncConfig(git_commit_message="")
        git_ops = GitOperations(config)
        
        # Empty commit message should fall back to default
        assert git_ops.config.git_commit_message == "Sync git with iCloud Drive"

    def test_edge_case_very_long_paths(self):
        """Test behavior with very long repository paths."""
        long_path = "/very/long/path/" + "subdir/" * 50 + "repo"
        config = SyncConfig(git_repo_path=long_path)
        git_ops = GitOperations(config)
        
        assert git_ops.git_repo_path == long_path

    def test_edge_case_special_characters_in_credentials(self):
        """Test URL generation with special characters in credentials."""
        config = SyncConfig(
            git_remote_url="https://github.com/test/repo.git",
            git_username="user@domain.com",
            git_pat="token!@#$%^&*()",
            git_repo_path="/tmp/test"
        )
        git_ops = GitOperations(config)
        
        auth_url = git_ops._get_auth_url()
        expected = "https://user@domain.com:token!@#$%^&*()@github.com/test/repo.git"
        assert auth_url == expected
