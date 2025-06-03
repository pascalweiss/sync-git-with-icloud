"""Configuration module for sync-icloud-git."""
import argparse
import os


class SyncConfig:
    """Configuration for sync-icloud-git.
    
    This class serves as a Data Transfer Object (DTO) for configuration settings.
    """
    
    # Default git repository path within project directory
    DEFAULT_GIT_REPO_PATH = os.path.join(os.getcwd(), "synced_repo")
    
    def __init__(self, git_remote_url=None, git_username=None, git_pat=None, git_repo_path=None, rclone_config_content=None, rclone_remote_folder=None):
        self.git_remote_url = git_remote_url
        self.git_username = git_username
        self.git_pat = git_pat
        self.git_repo_path = git_repo_path if git_repo_path else self.DEFAULT_GIT_REPO_PATH
        self.rclone_config_content = rclone_config_content
        self.rclone_remote_folder = rclone_remote_folder
    
    @classmethod
    def load_config(cls):
        """Load configuration from command line arguments, environment variables, or defaults.
        
        Returns:
            SyncConfig: A configuration object.
        """
        # Check environment variables first
        env_remote_url = os.environ.get("SYNC_ICLOUD_GIT__GIT_REMOTE_URL")
        env_username = os.environ.get("SYNC_ICLOUD_GIT__GIT_USERNAME")
        env_pat = os.environ.get("SYNC_ICLOUD_GIT__GIT_PAT")
        env_repo_path = os.environ.get("SYNC_ICLOUD_GIT__GIT_REPO_PATH")
        env_rclone_config = os.environ.get("SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT")
        env_rclone_remote_folder = os.environ.get("SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER")
        
        parser = argparse.ArgumentParser(description="Sync iCloud Git repository.")
        parser.add_argument(
            "--git-remote-url",
            type=str,
            help="The repository URL to sync with iCloud.",
            required=not bool(env_remote_url),  # Only required if not in environment
            default=env_remote_url,
        )
        parser.add_argument(
            "--git-username",
            type=str,
            help="The Git username for authentication.",
            required=not bool(env_username),  # Only required if not in environment
            default=env_username,
        )
        parser.add_argument(
            "--git-pat",
            type=str,
            help="The Git Personal Access Token for authentication.",
            required=not bool(env_pat),  # Only required if not in environment
            default=env_pat,
        )
        parser.add_argument(
            "--git-repo-path",
            type=str,
            help="The local path where the git repository will be stored.",
            required=False,
            default=env_repo_path if env_repo_path else cls.DEFAULT_GIT_REPO_PATH,
        )
        parser.add_argument(
            "--rclone-config-content",
            type=str,
            help="The rclone configuration content for iCloud access.",
            required=not bool(env_rclone_config),  # Only required if not in environment
            default=env_rclone_config,
        )
        parser.add_argument(
            "--rclone-remote-folder",
            type=str,
            help="The remote folder path in iCloud to sync with.",
            required=not bool(env_rclone_remote_folder),  # Only required if not in environment
            default=env_rclone_remote_folder,
        )
        args = parser.parse_args()
        
        # Validate required arguments
        if not args.git_remote_url:
            parser.error("Git remote URL is required. Provide it with --git-remote-url or set SYNC_ICLOUD_GIT__GIT_REMOTE_URL environment variable.")
        
        if not args.git_username:
            parser.error("Git username is required. Provide it with --git-username or set SYNC_ICLOUD_GIT__GIT_USERNAME environment variable.")
        
        if not args.git_pat:
            parser.error("Git Personal Access Token is required. Provide it with --git-pat or set SYNC_ICLOUD_GIT__GIT_PAT environment variable.")
        
        if not args.rclone_config_content:
            parser.error("Rclone configuration content is required. Provide it with --rclone-config-content or set SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT environment variable.")
        
        if not args.rclone_remote_folder:
            parser.error("Rclone remote folder is required. Provide it with --rclone-remote-folder or set SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER environment variable.")
            
        return cls(git_remote_url=args.git_remote_url, git_username=args.git_username, git_pat=args.git_pat, git_repo_path=args.git_repo_path, rclone_config_content=args.rclone_config_content, rclone_remote_folder=args.rclone_remote_folder)
    
    def __repr__(self):
        """Return a string representation of the configuration.
        
        Returns:
            str: A string representation of the configuration.
        """
        # Mask the PAT if it exists for security
        pat_display = "********" if self.git_pat else "None"
        rclone_display = "********" if self.rclone_config_content else "None"
        return f"SyncConfig(git_remote_url='{self.git_remote_url}', git_username='{self.git_username}', git_pat='{pat_display}', git_repo_path='{self.git_repo_path}', rclone_config_content='{rclone_display}', rclone_remote_folder='{self.rclone_remote_folder}')"