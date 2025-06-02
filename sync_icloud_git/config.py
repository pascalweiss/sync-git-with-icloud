"""Configuration module for sync-icloud-git."""
import argparse
import os


class SyncConfig:
    """Configuration for sync-icloud-git.
    
    This class serves as a Data Transfer Object (DTO) for configuration settings.
    """
    
    def __init__(self, git_remote_url=None, git_username=None, git_pat=None):
        self.git_remote_url = git_remote_url
        self.git_username = git_username
        self.git_pat = git_pat
    
    @classmethod
    def load_config(cls):
        """Load configuration from command line arguments, environment variables, or defaults.
        
        Returns:
            SyncConfig: A configuration object.
        """
        parser = argparse.ArgumentParser(description="Sync iCloud Git repository.")
        parser.add_argument(
            "--git-remote-url",
            type=str,
            help="The repository URL to sync with iCloud.",
            required=False,
            default=os.environ.get("SYNC_ICLOUD_GIT_REMOTE_URL"),
        )
        parser.add_argument(
            "--git-username",
            type=str,
            help="The Git username for authentication.",
            required=False,
            default=os.environ.get("SYNC_ICLOUD_GIT_USERNAME"),
        )
        parser.add_argument(
            "--git-pat",
            type=str,
            help="The Git Personal Access Token for authentication.",
            required=False,
            default=os.environ.get("SYNC_ICLOUD_GIT_PAT"),
        )
        args = parser.parse_args()
        
        # Validate required arguments
        if not args.git_remote_url:
            parser.error("Git remote URL is required. Provide it with --git-remote-url or set SYNC_ICLOUD_GIT_REMOTE_URL environment variable.")
            
        return cls(git_remote_url=args.git_remote_url, git_username=args.git_username, git_pat=args.git_pat)
    
    def __repr__(self):
        """Return a string representation of the configuration.
        
        Returns:
            str: A string representation of the configuration.
        """
        # Mask the PAT if it exists for security
        pat_display = "********" if self.git_pat else "None"
        return f"SyncConfig(git_remote_url='{self.git_remote_url}', git_username='{self.git_username}', git_pat='{pat_display}')"