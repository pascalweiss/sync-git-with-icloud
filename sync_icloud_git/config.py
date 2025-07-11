"""Configuration module for sync-icloud-git."""
import argparse
import os


class SyncConfig:
    """Configuration for sync-icloud-git.
    
    This class serves as a Data Transfer Object (DTO) for configuration settings.
    """
    
    # Default git repository path within project directory
    DEFAULT_GIT_REPO_PATH = os.path.join(os.getcwd(), "synced_repo")
    
    # Default git commit message
    DEFAULT_GIT_COMMIT_MESSAGE = "Sync git with iCloud Drive"
    
    # Default git commit author settings
    DEFAULT_GIT_COMMIT_USERNAME = "Sync Bot"
    DEFAULT_GIT_COMMIT_EMAIL = "sync-bot@example.com"
    
    # Default patterns to exclude from iCloud sync. Note, that these patterns are wrapped in single quotes 
    # to ensure they are treated as strings later in the rclone command.
    DEFAULT_EXCLUDE_PATTERNS = [
        "'.git/'",       
        "'.git'",
        "'.git/**'",
        "'**/.git'",
        "'**/.git/**'",
        "'.gitmodules'",
        "'**/.gitmodules'",
        "'.gitignore'",
        "'**/.gitignore'",
        "'.gitlab-ci.yml'",
        "'**/.gitlab-ci.yml'",
    ]
    
    def __init__(self, git_remote_url=None, git_username=None, git_pat=None, git_repo_path=None, git_commit_message=None, git_commit_username=None, git_commit_email=None, rclone_config_content=None, rclone_remote_folder=None, exclude_patterns=None, step=None, verbose=False):
        """Initialize the SyncConfig object with provided or default values."""
        self.git_remote_url = git_remote_url
        self.git_username = git_username
        self.git_pat = git_pat
        self.git_repo_path = git_repo_path if git_repo_path else self.DEFAULT_GIT_REPO_PATH
        self.git_commit_message = git_commit_message if git_commit_message else self.DEFAULT_GIT_COMMIT_MESSAGE
        self.git_commit_username = git_commit_username if git_commit_username else self.DEFAULT_GIT_COMMIT_USERNAME
        self.git_commit_email = git_commit_email if git_commit_email else self.DEFAULT_GIT_COMMIT_EMAIL
        self.rclone_config_content = rclone_config_content
        self.rclone_remote_folder = rclone_remote_folder
        self.exclude_patterns = exclude_patterns if exclude_patterns else self.DEFAULT_EXCLUDE_PATTERNS.copy()
        self.step = step if step else 'all'
        self.verbose = verbose
    
    @classmethod
    def load_config(cls):
        """Load configuration from command line arguments, environment variables, or defaults.
        
        Returns:
            SyncConfig: A configuration object.
        """
        # Check environment variables first
        env_remote_url = os.environ.get("SYNC_ICLOUD_GIT__GIT_REMOTE_URL")
        env_username = os.environ.get("SYNC_ICLOUD_GIT__GIT_USERNAME")
        env_pat = os.environ.get("SYNC_ICLOUD_GIT__GIT_PAT")
        env_repo_path = os.environ.get("SYNC_ICLOUD_GIT__GIT_REPO_PATH")
        env_commit_message = os.environ.get("SYNC_ICLOUD_GIT__GIT_COMMIT_MESSAGE")
        env_commit_username = os.environ.get("SYNC_ICLOUD_GIT__GIT_COMMIT_USERNAME")
        env_commit_email = os.environ.get("SYNC_ICLOUD_GIT__GIT_COMMIT_EMAIL")
        env_rclone_config = os.environ.get("SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT")
        env_rclone_remote_folder = os.environ.get("SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER")
        
        parser = argparse.ArgumentParser(description="Sync iCloud Git repository.")
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output for debugging and detailed information."
        )
        parser.add_argument(
            "--step",
            type=str,
            choices=['all', 'clone', 'update', 'sync'],
            default='all',
            help="Which step(s) to execute: 'all' (default), 'clone' (clone repo only), 'update' (update existing repo only), or 'sync' (sync from iCloud only)."
        )
        parser.add_argument(
            "--exclude-patterns",
            type=str,
            nargs='*',
            help="Additional patterns to exclude from iCloud sync (beyond defaults like .git, .DS_Store, etc.)."
        )
        parser.add_argument(
            "--git-remote-url",
            type=str,
            help="The repository URL to sync with iCloud.",
            required=not bool(env_remote_url),  # Only required if not in environment
            default=env_remote_url,
        )
        parser.add_argument(
            "--git-username",
            type=str,
            help="The Git username for authentication.",
            required=not bool(env_username),  # Only required if not in environment
            default=env_username,
        )
        parser.add_argument(
            "--git-pat",
            type=str,
            help="The Git Personal Access Token for authentication.",
            required=not bool(env_pat),  # Only required if not in environment
            default=env_pat,
        )
        parser.add_argument(
            "--git-repo-path",
            type=str,
            help="The local path where the git repository will be stored.",
            required=False,
            default=env_repo_path if env_repo_path else cls.DEFAULT_GIT_REPO_PATH,
        )
        parser.add_argument(
            "--git-commit-message",
            type=str,
            help="The commit message to use when committing changes.",
            required=False,
            default=env_commit_message if env_commit_message else cls.DEFAULT_GIT_COMMIT_MESSAGE,
        )
        parser.add_argument(
            "--git-commit-username",
            type=str,
            help="The username to use for git commits (git user.name).",
            required=False,
            default=env_commit_username if env_commit_username else cls.DEFAULT_GIT_COMMIT_USERNAME,
        )
        parser.add_argument(
            "--git-commit-email",
            type=str,
            help="The email to use for git commits (git user.email).",
            required=False,
            default=env_commit_email if env_commit_email else cls.DEFAULT_GIT_COMMIT_EMAIL,
        )
        parser.add_argument(
            "--rclone-config-content",
            type=str,
            help="The rclone configuration content for iCloud access.",
            required=not bool(env_rclone_config),  # Only required if not in environment
            default=env_rclone_config,
        )
        parser.add_argument(
            "--rclone-remote-folder",
            type=str,
            help="The remote folder path in iCloud to sync with.",
            required=not bool(env_rclone_remote_folder),  # Only required if not in environment
            default=env_rclone_remote_folder,
        )
        args = parser.parse_args()
        
        # Validate required arguments
        if not args.git_remote_url:
            parser.error("Git remote URL is required. Provide it with --git-remote-url or set SYNC_ICLOUD_GIT__GIT_REMOTE_URL environment variable.")
        
        if not args.git_username:
            parser.error("Git username is required. Provide it with --git-username or set SYNC_ICLOUD_GIT__GIT_USERNAME environment variable.")
        
        if not args.git_pat:
            parser.error("Git Personal Access Token is required. Provide it with --git-pat or set SYNC_ICLOUD_GIT__GIT_PAT environment variable.")
        
        if not args.rclone_config_content:
            parser.error("Rclone configuration content is required. Provide it with --rclone-config-content or set SYNC_ICLOUD_GIT__RCLONE_CONFIG_CONTENT environment variable.")
        
        if not args.rclone_remote_folder:
            parser.error("Rclone remote folder is required. Provide it with --rclone-remote-folder or set SYNC_ICLOUD_GIT__RCLONE_REMOTE_FOLDER environment variable.")
        
        # Handle exclude patterns (combine defaults with any additional ones)
        exclude_patterns = cls.DEFAULT_EXCLUDE_PATTERNS.copy()
        if args.exclude_patterns:
            exclude_patterns.extend(args.exclude_patterns)
            
        return cls(
            git_remote_url=args.git_remote_url, 
            git_username=args.git_username, 
            git_pat=args.git_pat, 
            git_repo_path=args.git_repo_path, 
            git_commit_message=args.git_commit_message,
            git_commit_username=args.git_commit_username,
            git_commit_email=args.git_commit_email,
            rclone_config_content=args.rclone_config_content, 
            rclone_remote_folder=args.rclone_remote_folder,
            exclude_patterns=exclude_patterns,
            step=args.step,
            verbose=args.verbose
        )
    
    def __repr__(self):
        """Return a string representation of the configuration.
        
        Returns:
            str: A string representation of the configuration.
        """
        # Mask the PAT if it exists for security
        pat_display = "********" if self.git_pat else "None"
        rclone_display = "********" if self.rclone_config_content else "None"
        exclude_count = len(self.exclude_patterns) if self.exclude_patterns else 0
        return f"SyncConfig(git_remote_url='{self.git_remote_url}', git_username='{self.git_username}', git_pat='{pat_display}', git_repo_path='{self.git_repo_path}', git_commit_message='{self.git_commit_message}', git_commit_username='{self.git_commit_username}', git_commit_email='{self.git_commit_email}', rclone_config_content='{rclone_display}', rclone_remote_folder='{self.rclone_remote_folder}', exclude_patterns={exclude_count} patterns, step='{self.step}', verbose={self.verbose})"