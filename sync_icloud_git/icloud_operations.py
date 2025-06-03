"""iCloud operations module for sync-icloud-git."""
import os
import tempfile
import shutil
import subprocess
from rclone_python import rclone


class ICloudOperations:
    """Class for handling iCloud operations (READ-ONLY from iCloud)."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.git_repo_path = config.git_repo_path
        self.rclone_config_content = config.rclone_config_content
        self.rclone_remote_folder = config.rclone_remote_folder
        
        # Setup rclone configuration
        self.rclone_config_file = None
        self._setup_rclone_config()
        
        print(f"iCloud operations configured (READ-ONLY mode) for path: {self.git_repo_path}")
        print(f"iCloud remote folder: {self.rclone_remote_folder}")

    # PUBLIC METHODS
    
    def test_icloud_connection(self):
        """Test connection to iCloud remote folder and return file count.
        
        Returns:
            int: Number of items found in the iCloud folder
            
        Raises:
            Exception: If connection fails or remote folder is not accessible
        """
        print("🔍 Testing iCloud connection...")
        remote_path = self._build_remote_path()
        
        try:
            # Use explicit config file for the test
            files = rclone.ls(remote_path, args=['--config', self.rclone_config_file.name])
            file_count = len(files)
            print(f"✅ Found {file_count} items in iCloud folder")
            return file_count
        except Exception as e:
            print(f"❌ Failed to connect to iCloud folder '{self.rclone_remote_folder}': {e}")
            raise

    def sync_from_icloud_to_repo(self):
        """Sync files from iCloud to local git repository (iCloud remains unchanged).
        Files that are not already in the git repository will be copied.
        Files that also exist in the git repository but that have changed will be updated.
        Files that have been removed from iCloud will be removed from the git repository.
        In the end, the git repository will be in sync with iCloud
        """
        print(f"🔄 Starting sync from iCloud folder '{self.rclone_remote_folder}' to '{self.git_repo_path}'")
        
        # Orchestrate the sync process using private methods
        remote_path = self._build_remote_path()
        self.test_icloud_connection()
        self._execute_sync_operation(remote_path)
        
        print("✅ Sync completed successfully!")
        print(f"📁 Synced iCloud folder to git repository")

    # PRIVATE METHODS - Configuration Management
    
    def _setup_rclone_config(self):
        """Setup rclone configuration file from config content."""
        # Create a temporary config file for rclone
        self.rclone_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
        self.rclone_config_file.write(self.rclone_config_content)
        self.rclone_config_file.flush()  # Ensure content is written to disk
        self.rclone_config_file.close()
        
        # Verify the config file was written correctly
        with open(self.rclone_config_file.name, 'r') as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Rclone config file is empty after write")
        
        print(f"Rclone config setup at: {self.rclone_config_file.name} ({len(content)} chars)")

    def _cleanup_rclone_config(self):
        """Clean up temporary rclone configuration file."""
        if self.rclone_config_file and os.path.exists(self.rclone_config_file.name):
            os.unlink(self.rclone_config_file.name)
            print("Cleaned up rclone config file")

    # PRIVATE METHODS - Path and Remote Operations
    
    def _build_remote_path(self):
        """Build the rclone remote path for iCloud.
        
        Returns:
            str: The formatted remote path for rclone
        """
        return f"iclouddrive:{self.rclone_remote_folder}"

    # PRIVATE METHODS - Sync Operations
    
    def _execute_sync_operation(self, remote_path):
        """Execute the actual rclone sync operation with error handling.
        
        Args:
            remote_path (str): The source remote path
        """
        print(f"📂 Syncing from {remote_path} to {self.git_repo_path}...")
        
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
            '-v'
        ]
        
        # Add exclude patterns
        for pattern in self.config.exclude_patterns:
            args.extend(['--exclude', pattern])
        
        print(f"🚫 Excluding {len(self.config.exclude_patterns)} patterns")
        
        self._log_sync_parameters(remote_path, args)
        
        # Clear the environment variable to force using config file
        old_config = os.environ.get('RCLONE_CONFIG')
        if 'RCLONE_CONFIG' in os.environ:
            del os.environ['RCLONE_CONFIG']
        
        try:
            # Use subprocess as fallback due to rclone_python library hanging issues
            success = self._execute_sync_with_subprocess(remote_path, args)
            if success:
                print("✅ Sync completed without errors")
            else:
                print("⚠️ Sync may have failed, verifying results...")
                self._verify_sync_results()
        except Exception as e:
            # Handle any unexpected errors
            print(f"❌ Sync operation failed with exception: {e}")
            self._verify_sync_results()
        finally:
            # Restore environment variable if it existed
            if old_config:
                os.environ['RCLONE_CONFIG'] = old_config

    def _log_sync_parameters(self, remote_path, args):
        """Log the sync parameters for debugging purposes.
        
        Args:
            remote_path (str): The source remote path
            args (list): Command line arguments for rclone
        """
        print(f"🔧 DEBUG: rclone.sync parameters:")
        print(f"   src_path: '{remote_path}'")
        print(f"   dest_path: '{self.git_repo_path}'")
        print(f"   show_progress: True")
        print(f"   args: {args}")
        print(f"   exclude_patterns from config: {self.config.exclude_patterns}")

    def _execute_sync_with_subprocess(self, remote_path, args):
        """Execute rclone sync using subprocess instead of rclone_python.
        
        Args:
            remote_path (str): The source remote path
            args (list): Command line arguments for rclone
        
        Returns:
            bool: True if sync succeeded, False otherwise
        """
        # Build the complete rclone command
        cmd = ['rclone', 'sync', remote_path, self.git_repo_path] + args
        
        print(f"🔧 Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.stdout:
                print(f"📝 rclone output: {result.stdout}")
            
            if result.stderr:
                print(f"⚠️ rclone stderr: {result.stderr}")
            
            # rclone returns 0 on success
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Sync operation timed out after 5 minutes")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ rclone command failed with return code {e.returncode}")
            if e.stdout:
                print(f"   stdout: {e.stdout}")
            if e.stderr:
                print(f"   stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error running rclone: {e}")
            return False

    def _verify_sync_results(self):
        """Verify sync results by comparing expected vs actual file counts."""
        # Get expected file count from iCloud
        try:
            remote_path = self._build_remote_path()
            remote_files = rclone.ls(remote_path, args=['--config', self.rclone_config_file.name])
            expected_count = len(remote_files)
        except Exception as e:
            print(f"⚠️ Could not get expected file count from iCloud: {e}")
            expected_count = 0
            
        # Count actual synced files
        synced_files = self._count_synced_files()
        actual_count = len(synced_files)
        
        print(f"📊 Sync verification: Expected {expected_count} files, Found {actual_count} files")
        
        if actual_count > 0 and actual_count >= expected_count:
            print(f"✅ Sync verification passed! Successfully synced {actual_count} files")
        elif actual_count > 0:
            print(f"⚠️ Partial sync: Found {actual_count} files but expected {expected_count}")
        else:
            print(f"❌ Sync verification failed: No files found (expected {expected_count})")
            raise Exception(f"Sync failed - no files were synced")

    def _handle_sync_error(self, error):
        """Handle sync errors by verifying if sync actually succeeded.
        
        Args:
            error (Exception): The exception raised during sync
            
        Raises:
            Exception: If sync actually failed
        """
        print(f"⚠️  rclone reported an error, verifying sync result...")
        
        # Use the new verification method
        try:
            self._verify_sync_results()
        except Exception:
            # If verification fails, re-raise the original error
            print(f"❌ Sync verification failed: {error}")
            raise error

    def _count_synced_files(self):
        """Count files in the destination directory (excluding .git).
        
        Returns:
            list: List of synced file paths
        """
        synced_files = []
        if os.path.exists(self.git_repo_path):
            for root, dirs, files in os.walk(self.git_repo_path):
                # Skip .git directory
                if '.git' in root:
                    continue
                for file in files:
                    if not file.startswith('.git'):
                        synced_files.append(os.path.join(root, file))
        return synced_files

    def __repr__(self):
        return f"ICloudOperations(git_repo_path='{self.git_repo_path}', rclone_remote_folder='{self.rclone_remote_folder}')"
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self._cleanup_rclone_config()
        except Exception:
            pass  # Ignore cleanup errors during destruction
