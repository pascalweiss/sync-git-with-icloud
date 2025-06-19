"""Tests for config.py module."""
import os
import pytest
import tempfile
from unittest.mock import patch, Mock
from sync_icloud_git.config import SyncConfig


class TestSyncConfig:
    """Test cases for SyncConfig class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = SyncConfig()
        
        assert config.git_repo_path == SyncConfig.DEFAULT_GIT_REPO_PATH
        assert config.git_commit_message == SyncConfig.DEFAULT_GIT_COMMIT_MESSAGE
        assert config.git_commit_username == SyncConfig.DEFAULT_GIT_COMMIT_USERNAME
        assert config.git_commit_email == SyncConfig.DEFAULT_GIT_COMMIT_EMAIL
        assert config.exclude_patterns == SyncConfig.DEFAULT_EXCLUDE_PATTERNS
        assert config.step == 'all'
        assert config.git_remote_url is None
        assert config.git_username is None
        assert config.git_pat is None
        assert config.rclone_config_content is None
        assert config.rclone_remote_folder is None

    def test_default_constants(self):
        """Test that default constants are properly defined."""
        assert SyncConfig.DEFAULT_GIT_COMMIT_MESSAGE == "Sync git with iCloud Drive"
        assert SyncConfig.DEFAULT_GIT_COMMIT_USERNAME == "Sync Bot"
        assert SyncConfig.DEFAULT_GIT_COMMIT_EMAIL == "sync-bot@example.com"
        assert isinstance(SyncConfig.DEFAULT_EXCLUDE_PATTERNS, list)
        assert len(SyncConfig.DEFAULT_EXCLUDE_PATTERNS) > 0
        assert "'.git/'" in SyncConfig.DEFAULT_EXCLUDE_PATTERNS
        assert "'.gitignore'" in SyncConfig.DEFAULT_EXCLUDE_PATTERNS

    def test_custom_values_override_defaults(self):
        """Test that custom values override defaults."""
        custom_repo_path = "/custom/path/repo"
        custom_commit_message = "Custom commit message"
        custom_exclude_patterns = ["'custom_pattern'"]
        
        config = SyncConfig(
            git_remote_url="https://test.com/repo.git",
            git_username="testuser",
            git_pat="testtoken",
            git_repo_path=custom_repo_path,
            git_commit_message=custom_commit_message,
            rclone_config_content="test_config",
            rclone_remote_folder="test_folder",
            exclude_patterns=custom_exclude_patterns,
            step="clone"
        )
        
        assert config.git_remote_url == "https://test.com/repo.git"
        assert config.git_username == "testuser"
        assert config.git_pat == "testtoken"
        assert config.git_repo_path == custom_repo_path
        assert config.git_commit_message == custom_commit_message
        assert config.rclone_config_content == "test_config"
        assert config.rclone_remote_folder == "test_folder"
        assert config.exclude_patterns == custom_exclude_patterns
        assert config.step == "clone"

    def test_none_values_use_defaults(self):
        """Test that None values fall back to defaults."""
        config = SyncConfig(
            git_repo_path=None,
            git_commit_message=None,
            exclude_patterns=None,
            step=None
        )
        
        assert config.git_repo_path == SyncConfig.DEFAULT_GIT_REPO_PATH
        assert config.git_commit_message == SyncConfig.DEFAULT_GIT_COMMIT_MESSAGE
        assert config.exclude_patterns == SyncConfig.DEFAULT_EXCLUDE_PATTERNS
        assert config.step == 'all'

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_with_all_env_vars(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__GIT_REPO_PATH': '/env/repo/path',
            'SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE': 'Env commit message',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SyncConfig.load_config()
            
            assert config.git_remote_url == 'https://env.test.com/repo.git'
            assert config.git_username == 'envuser'
            assert config.git_pat == 'envtoken'
            assert config.git_repo_path == '/env/repo/path'
            assert config.git_commit_message == 'Env commit message'
            assert config.rclone_config_content == 'env_rclone_config'
            assert config.rclone_remote_folder == 'env_folder'

    @patch('sys.argv', ['sync-icloud-git', '--step=clone'])
    def test_load_config_with_command_line_args(self):
        """Test loading configuration from command line arguments."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SyncConfig.load_config()
            assert config.step == 'clone'

    @patch('sys.argv', ['sync-icloud-git', '--git-commit-message', 'CLI commit message'])
    def test_load_config_cli_overrides_env(self):
        """Test that CLI arguments override environment variables."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE': 'Env commit message',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SyncConfig.load_config()
            assert config.git_commit_message == 'CLI commit message'

    @patch('sys.argv', ['sync-icloud-git', '--exclude-patterns', 'pattern1', 'pattern2'])
    def test_load_config_with_exclude_patterns(self):
        """Test loading configuration with additional exclude patterns."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SyncConfig.load_config()
            
            # Should contain default patterns plus additional ones
            assert len(config.exclude_patterns) == len(SyncConfig.DEFAULT_EXCLUDE_PATTERNS) + 2
            assert 'pattern1' in config.exclude_patterns
            assert 'pattern2' in config.exclude_patterns
            # Should still contain default patterns
            assert "'.git/'" in config.exclude_patterns

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_missing_required_args(self):
        """Test that missing required arguments raise appropriate errors."""
        # Clear environment variables
        env_vars = {}
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_missing_git_remote_url(self):
        """Test error when git remote URL is missing."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_missing_git_username(self):
        """Test error when git username is missing."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_missing_git_pat(self):
        """Test error when git PAT is missing."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_missing_rclone_config(self):
        """Test error when rclone config is missing."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    @patch('sys.argv', ['sync-icloud-git'])
    def test_load_config_missing_rclone_remote_folder(self):
        """Test error when rclone remote folder is missing."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    def test_repr_masks_sensitive_data(self):
        """Test that __repr__ masks sensitive information."""
        config = SyncConfig(
            git_remote_url="https://test.com/repo.git",
            git_username="testuser",
            git_pat="secret_token_12345",
            git_commit_message="Test commit",
            rclone_config_content="secret_rclone_config_content"
        )
        
        repr_str = repr(config)
        
        # Should contain non-sensitive data
        assert "https://test.com/repo.git" in repr_str
        assert "testuser" in repr_str
        assert "Test commit" in repr_str
        
        # Should mask sensitive data
        assert "secret_token_12345" not in repr_str
        assert "secret_rclone_config_content" not in repr_str
        assert "********" in repr_str

    def test_repr_handles_none_values(self):
        """Test that __repr__ handles None values correctly."""
        config = SyncConfig()
        repr_str = repr(config)
        
        # Should contain "None" for PAT when it's None
        assert "git_pat='None'" in repr_str or 'git_pat="None"' in repr_str

    def test_step_choices_validation(self):
        """Test that step parameter accepts valid choices."""
        valid_steps = ['all', 'clone', 'update', 'sync']
        
        for step in valid_steps:
            config = SyncConfig(step=step)
            assert config.step == step

    @patch('sys.argv', ['sync-icloud-git', '--step=invalid'])
    def test_invalid_step_choice(self):
        """Test that invalid step choice raises error."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://env.test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'envuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'envtoken',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'env_rclone_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'env_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            with pytest.raises(SystemExit):
                SyncConfig.load_config()

    def test_exclude_patterns_copy_behavior(self):
        """Test that exclude patterns are properly copied and don't affect defaults."""
        # Create config with default patterns
        config1 = SyncConfig()
        original_default_count = len(SyncConfig.DEFAULT_EXCLUDE_PATTERNS)
        
        # Modify the instance patterns
        config1.exclude_patterns.append("'new_pattern'")
        
        # Create another config and verify defaults weren't affected
        config2 = SyncConfig()
        assert len(config2.exclude_patterns) == original_default_count
        assert "'new_pattern'" not in config2.exclude_patterns
        
        # Verify the default list itself wasn't modified
        assert len(SyncConfig.DEFAULT_EXCLUDE_PATTERNS) == original_default_count

    def test_git_repo_path_default_behavior(self):
        """Test git repo path default behavior."""
        config = SyncConfig()
        
        # Should use the default path
        assert config.git_repo_path == SyncConfig.DEFAULT_GIT_REPO_PATH
        assert config.git_repo_path.endswith("synced_repo")

    def test_config_immutability_after_creation(self):
        """Test that configuration values can be modified after creation."""
        config = SyncConfig(git_commit_message="Original message")
        assert config.git_commit_message == "Original message"
        
        # Should be able to modify after creation (not immutable)
        config.git_commit_message = "Modified message"
        assert config.git_commit_message == "Modified message"

    @patch('sys.argv', ['sync-icloud-git'])
    def test_git_commit_identity_environment_variables(self):
        """Test that git commit username and email are loaded from environment variables."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'testuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'testtoken',
            'SYNC_ICLOUD_GIT__GIT_COMMIT_USERNAME': 'Environment User',
            'SYNC_ICLOUD_GIT__GIT_COMMIT_EMAIL': 'env-user@example.com',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'test_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'test_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SyncConfig.load_config()
            
            # Test that environment variables override defaults
            assert config.git_commit_username == 'Environment User'
            assert config.git_commit_email == 'env-user@example.com'
            
            # Test that other values are still loaded correctly
            assert config.git_remote_url == 'https://test.com/repo.git'
            assert config.git_username == 'testuser'
            assert config.git_pat == 'testtoken'

    @patch('sys.argv', [
        'sync-icloud-git', 
        '--git-commit-username', 'CLI User',
        '--git-commit-email', 'cli-user@example.com'
    ])
    def test_git_commit_identity_command_line_override(self):
        """Test that command line arguments override environment variables for git commit identity."""
        env_vars = {
            'SYNC_ICLOUD_GIT__GIT_REMOTE_URL': 'https://test.com/repo.git',
            'SYNC_ICLOUD_GIT__GIT_USERNAME': 'testuser',
            'SYNC_ICLOUD_GIT__GIT_PAT': 'testtoken',
            'SYNC_ICLOUD_GIT__GIT_COMMIT_USERNAME': 'Environment User',
            'SYNC_ICLOUD_GIT__GIT_COMMIT_EMAIL': 'env-user@example.com',
            'SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT': 'test_config',
            'SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER': 'test_folder'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SyncConfig.load_config()
            
            # Test that CLI arguments override environment variables
            assert config.git_commit_username == 'CLI User'
            assert config.git_commit_email == 'cli-user@example.com'
            
            # Test that other environment variables are still used
            assert config.git_remote_url == 'https://test.com/repo.git'
            assert config.git_username == 'testuser'
            assert config.git_pat == 'testtoken'
            
            # Test priority: CLI > env vars > defaults
            # These should not be the environment values since CLI overrides them
            assert config.git_commit_username != 'Environment User'
            assert config.git_commit_email != 'env-user@example.com'
            
            # And they should not be the defaults since CLI overrides them
            assert config.git_commit_username != SyncConfig.DEFAULT_GIT_COMMIT_USERNAME
            assert config.git_commit_email != SyncConfig.DEFAULT_GIT_COMMIT_EMAIL
