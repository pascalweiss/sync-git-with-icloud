"""Command line interface for sync-icloud-git."""
from sync_icloud_git.config import SyncConfig

def main():
    """Run the main program."""
    config = SyncConfig.load_config()
    print(f"Configuration: {config}")

if __name__ == "__main__":
    main()
