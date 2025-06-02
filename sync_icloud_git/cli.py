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

if __name__ == "__main__":
    main()
