"""Cloud storage operations module for sync-icloud-git."""
import os
import tempfile
from rclone_python import rclone


class CloudSyncOperations:
    """Class for handling cloud storage operations (READ-ONLY from cloud storage).

    Supports any rclone backend including iCloud, Nextcloud, Google Drive, Dropbox, S3, etc.
    """

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.git_repo_path = config.git_repo_path
        self.rclone_config_content = config.rclone_config_content
        self.rclone_remote_folder = config.rclone_remote_folder
        self.rclone_remote_name = config.rclone_remote_name

        # Setup rclone configuration
        self.rclone_config_file = None
        self._setup_rclone_config()

        if config.verbose:
            print(f"Cloud sync configured: {self.rclone_remote_name}:{self.rclone_remote_folder} → {os.path.basename(self.git_repo_path)}")

    # PUBLIC METHODS

    def test_connection(self):
        """Test connection to cloud storage remote folder and return file count.

        Returns:
            int: Number of items found in the remote folder

        Raises:
            Exception: If connection fails or remote folder is not accessible
        """
        print("Testing cloud storage connection...")
        remote_path = self._build_remote_path()

        try:
            # Use explicit config file for the test
            files = rclone.ls(remote_path, args=['--config', self.rclone_config_file.name])
            file_count = len(files)
            print(f"✅ Found {file_count} items in remote folder")
            return file_count
        except (OSError, ValueError, RuntimeError) as e:
            print(f"❌ Failed to connect to remote folder '{self.rclone_remote_folder}': {e}")
            raise

    def sync_from_cloud_to_repo(self):
        """Sync files from cloud storage to local git repository (cloud storage remains unchanged).
        Files that are not already in the git repository will be copied.
        Files that also exist in the git repository but that have changed will be updated.
        Files that have been removed from cloud storage will be removed from the git repository.
        In the end, the git repository will be in sync with cloud storage.
        """
        print(f"Starting sync from remote folder '{self.rclone_remote_name}:{self.rclone_remote_folder}' to '{self.git_repo_path}'")

        # Orchestrate the sync process using private methods
        remote_path = self._build_remote_path()
        self.test_connection()
        self._execute_sync_operation(remote_path)

    # BACKWARD COMPATIBILITY ALIASES (deprecated)
    def test_icloud_connection(self):
        """Deprecated: Use test_connection() instead."""
        return self.test_connection()

    def sync_from_icloud_to_repo(self):
        """Deprecated: Use sync_from_cloud_to_repo() instead."""
        return self.sync_from_cloud_to_repo()

    # PRIVATE METHODS - Configuration Management

    def _setup_rclone_config(self):
        """Setup rclone configuration file from config content."""
        # Create a temporary config file for rclone
        self.rclone_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
        self.rclone_config_file.write(self.rclone_config_content)
        self.rclone_config_file.flush()  # Ensure content is written to disk
        self.rclone_config_file.close()

        # Verify the config file was written correctly
        with open(self.rclone_config_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Rclone config file is empty after write")

        if self.config.verbose:
            print(f"Rclone config ready ({len(content)} chars)")

    def _cleanup_rclone_config(self):
        """Clean up temporary rclone configuration file."""
        if self.rclone_config_file and os.path.exists(self.rclone_config_file.name):
            os.unlink(self.rclone_config_file.name)
            if self.config.verbose:
                print("Cleaned up rclone config file")

    # PRIVATE METHODS - Path and Remote Operations

    def _build_remote_path(self):
        """Build the rclone remote path for cloud storage.

        Returns:
            str: The formatted remote path for rclone
        """
        return f"{self.rclone_remote_name}:{self.rclone_remote_folder}"

    # PRIVATE METHODS - Sync Operations

    def _execute_sync_operation(self, remote_path):
        """Execute the actual rclone sync operation with error handling.

        Args:
            remote_path (str): The source remote path
        """
        # Ensure destination directory exists
        os.makedirs(self.git_repo_path, exist_ok=True)

        # Build command line arguments for rclone sync operation
        args = [
            '--config', self.rclone_config_file.name,  # Use explicit config file
            '--transfers', '3',
            '--checkers', '4',
            '--tpslimit', '10',
            '--retries', '5',
            '--low-level-retries', '10',
            '--delete-excluded=false',
            '--checksum',  # Use checksum comparison instead of modification time
            '-v'
        ]

        # Add exclude patterns as separate --exclude arguments
        if self.config.exclude_patterns:
            for pattern in self.config.exclude_patterns:
                args.extend(['--exclude', pattern])

        self._log_sync_parameters(remote_path, args)

        # Clear the environment variable to force using config file
        old_config = os.environ.get('RCLONE_CONFIG')
        if 'RCLONE_CONFIG' in os.environ:
            del os.environ['RCLONE_CONFIG']

        try:
            # Use rclone_python library directly (based on successful test_rclone.py approach)
            self._execute_sync_with_library(remote_path, args)
        except Exception as e:
            # If there's any error, the sync failed - don't try to verify
            print(f"❌ rclone sync failed: {e}")
            raise RuntimeError(f"Sync operation failed: {e}") from e
        finally:
            # Restore environment variable if it existed
            if old_config:
                os.environ['RCLONE_CONFIG'] = old_config

    def _log_sync_parameters(self, remote_path, args):
        """Log the sync parameters for debugging purposes.

        Args:
            remote_path (str): The source remote path
            args (list): Command line arguments for rclone (unused but kept for compatibility)
        """
        print(f"Syncing from {remote_path} to {self.git_repo_path}...")
        if self.config.exclude_patterns:
            if len(self.config.exclude_patterns) <= 10:
                # Show all patterns if 10 or fewer
                print(f"Excluding {len(self.config.exclude_patterns)} patterns: {', '.join(self.config.exclude_patterns)}")
            else:
                # Show first 8 with "..." if more than 10
                print(f"Excluding {len(self.config.exclude_patterns)} patterns: {', '.join(self.config.exclude_patterns[:8])}...")

    def _execute_sync_with_library(self, remote_path, args):
        """Execute rclone sync using rclone_python library (preferred approach).

        Args:
            remote_path (str): The source remote path
            args (list): Command line arguments for rclone
        """
        # Use rclone_python library directly (same approach as test_rclone.py)
        rclone.sync(
            src_path=remote_path,
            dest_path=self.git_repo_path,
            args=args,
            show_progress=True
        )

        print("✅ rclone sync completed!")
        # Quick file count for user feedback
        try:
            synced_files = self._count_synced_files()
            print(f"{len(synced_files)} files in repository")
        except (OSError, AttributeError):
            print(f"Sync to {os.path.basename(self.git_repo_path)} completed")

    def _count_synced_files(self):
        """Count files in the destination directory (excluding .git).

        Returns:
            list: List of synced file paths
        """
        synced_files = []
        if os.path.exists(self.git_repo_path):
            for root, _, files in os.walk(self.git_repo_path):
                # Skip .git directory
                if '.git' in root:
                    continue
                for file in files:
                    if not file.startswith('.git'):
                        synced_files.append(os.path.join(root, file))
        return synced_files

    def __repr__(self):
        return f"CloudSyncOperations(git_repo_path='{self.git_repo_path}', rclone_remote_name='{self.rclone_remote_name}', rclone_remote_folder='{self.rclone_remote_folder}')"

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self._cleanup_rclone_config()
        except (OSError, AttributeError):
            pass  # Ignore cleanup errors during destruction


# Backward compatibility alias
ICloudOperations = CloudSyncOperations
