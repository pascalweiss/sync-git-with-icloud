"""Git operations module for sync-icloud-git."""
import git
from sync_icloud_git.config import SyncConfig


class GitOperations:
    """Class for handling Git operations.
    
    This class provides functionality for interacting with Git repositories
    using the GitPython library.
    """
    
    def __init__(self, config):
        """Initialize the GitOperations with a configuration.
        
        Args:
            config (SyncConfig): The configuration object containing Git settings.
        """
        self.config = config
        # Store configuration values for convenience
        self.git_remote_url = config.git_remote_url
        self.git_username = config.git_username
        self.git_pat = config.git_pat
    
    def __repr__(self):
        """Return a string representation of the GitOperations instance.
        
        Returns:
            str: A string representation of the GitOperations.
        """
        return f"GitOperations(config={self.config})"
