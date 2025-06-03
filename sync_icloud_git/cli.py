"""Command line interface for sync-icloud-git."""
from sync_icloud_git.config import SyncConfig
from sync_icloud_git.git_operations import GitOperations
from sync_icloud_git.icloud_operations import ICloudOperations

def main():
    """Run the main program."""
    config = SyncConfig.load_config()
    print(f"Configuration: {config}")
    
    # Create an instance of GitOperations with the loaded configuration
    git_ops = GitOperations(config)
    print(f"GitOperations: {git_ops}")
    
    # Create an instance of ICloudOperations with the loaded configuration
    icloud_ops = ICloudOperations(config)
    print(f"ICloudOperations: {icloud_ops}")
    
    # Execute based on the step parameter
    if config.step in ['all', 'update']:
        # Check and update existing repository
        print("\n--- Checking for existing git repository ---")
        repo_updated = git_ops.check_and_update_repo()
        
        if repo_updated:
            print("✅ Repository update completed successfully!")
        elif config.step == 'all':
            # Only try to clone if we're doing 'all' steps
            print("ℹ️  No existing repository found at the specified path.")
            print("\n--- Cloning repository ---")
            clone_success = git_ops.clone_repo()
            if clone_success:
                print("✅ Repository cloned successfully!")
            else:
                print("❌ Failed to clone repository.")
                return
        else:
            print("ℹ️  No existing repository found. Use --step=clone or --step=all to clone first.")
            return
    
    elif config.step == 'clone':
        # Only clone the repository
        print("\n--- Cloning repository ---")
        clone_success = git_ops.clone_repo()
        if clone_success:
            print("✅ Repository cloned successfully!")
        else:
            print("❌ Failed to clone repository.")
            return
    
    # Sync from iCloud to git repository
    if config.step in ['all', 'sync']:
        print("\n--- Syncing from iCloud ---")
        try:
            icloud_ops.sync_from_icloud_to_repo()
            print("✅ iCloud sync completed successfully!")
        except Exception as e:
            print(f"❌ iCloud sync failed: {e}")
            return

if __name__ == "__main__":
    main()
