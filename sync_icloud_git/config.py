"""Configuration module for sync-icloud-git."""


class SyncConfig:
    """Configuration for sync-icloud-git.
    
    This class serves as a Data Transfer Object (DTO) for configuration settings.
    """
    
    def __init__(self, git_remote_url=None):
        """Initialize the configuration.
        
        Args:
            git_remote_url (str, optional): The Git remote URL to sync with iCloud.
        """
        self.git_remote_url = git_remote_url
    
    @classmethod
    def from_args(cls, args):
        """Create a configuration object from command line arguments.
        
        Args:
            args: The parsed command line arguments.
            
        Returns:
            SyncConfig: A configuration object.
        """
        return cls(
            git_remote_url=args.git_remote_url,
        )
    
    def __repr__(self):
        """Return a string representation of the configuration.
        
        Returns:
            str: A string representation of the configuration.
        """
        return f"SyncConfig(git_remote_url='{self.git_remote_url}')"