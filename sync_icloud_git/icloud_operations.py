"""iCloud operations module for sync-icloud-git."""


class ICloudOperations:
    """Class for handling iCloud operations (READ-ONLY from iCloud)."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.git_repo_path = config.git_repo_path
        
        print(f"iCloud operations configured (READ-ONLY mode) for path: {self.git_repo_path}")

    def sync_from_icloud_to_repo(self):
        """Sync files from iCloud to local git repository (iCloud remains unchanged).
        Files that are not already in the git repository will be copied.
        Files that also exist in the git repository but that have changed will be updated.
        Files that have been removed from iCloud will be removed from the git repository.
        In the end, the git repository will be in sync with iCloud
        """
        pass


    def __repr__(self):
        return f"ICloudOperations(git_repo_path='{self.git_repo_path}')"
