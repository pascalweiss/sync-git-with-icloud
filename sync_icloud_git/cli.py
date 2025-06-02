"""Command line interface for sync-icloud-git."""
import argparse
from sync_icloud_git.config import SyncConfig

def read_command_line_args():
    """Read command line arguments."""

    parser = argparse.ArgumentParser(description="Sync iCloud Git repository.")
    parser.add_argument(
        "--git-remote-url",
        type=str,
        help="The repository URL to sync with iCloud.",
        required=True,
    )
    return parser.parse_args()

def main():
    """Run the main program."""
    args = read_command_line_args()
    config = SyncConfig.from_args(args)
    print(f"Configuration: {config}")

if __name__ == "__main__":
    main()
