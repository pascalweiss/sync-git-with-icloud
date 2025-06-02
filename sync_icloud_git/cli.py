"""Command line interface for sync-icloud-git."""
from sync_icloud_git.config import SyncConfig
from sync_icloud_git.git_operations import GitOperations

def main():
    """Run the main program."""
    config = SyncConfig.load_config()
    print(f"Configuration: {config}")
    
    # Create an instance of GitOperations with the loaded configuration
    git_ops = GitOperations(config)
    print(f"GitOperations: {git_ops}")
    
    # Check and update existing repository
    print("\n--- Checking for existing git repository ---")
    repo_updated = git_ops.check_and_update_repo()
    
    if repo_updated:
        print("✅ Repository update completed successfully!")
    else:
        print("ℹ️  No existing repository found at the specified path.")
        print("\n--- Cloning repository ---")
        clone_success = git_ops.clone_repo()
        if clone_success:
            print("✅ Repository cloned successfully!")
        else:
            print("❌ Failed to clone repository.")

if __name__ == "__main__":
    main()
