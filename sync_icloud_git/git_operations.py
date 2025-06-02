"""Git operations module for sync-icloud-git."""
import git
import os
from sync_icloud_git.config import SyncConfig


class GitOperations:
    """Class for handling Git operations.
    
    This class provides functionality for interacting with Git repositories
    using the GitPython library.
    """
    
    def __init__(self, config):
        """Initialize the GitOperations with a configuration.
        
        Args:
            config (SyncConfig): The configuration object containing Git settings.
        """
        self.config = config
        # Store configuration values for convenience
        self.git_remote_url = config.git_remote_url
        self.git_username = config.git_username
        self.git_pat = config.git_pat
        self.git_repo_path = config.git_repo_path
        
        # Configure Git authentication if credentials are provided
        self._configure_git_auth()
    
    def _configure_git_auth(self):
        """Configure Git authentication using the provided credentials."""
        if self.git_username and self.git_pat:
            print(f"Git authentication configured for user: {self.git_username}")
        else:
            print("Warning: No Git credentials provided - operations may fail for private repositories")
    
    def _get_authenticated_remote_url(self):
        """Get the remote URL with embedded authentication credentials.
        
        Returns:
            str: URL with embedded authentication credentials for HTTPS repos
        """
        if not self.git_username or not self.git_pat:
            return self.git_remote_url
            
        # Handle different URL formats
        if self.git_remote_url.startswith('https://'):
            # For HTTPS URLs, embed credentials
            # Format: https://username:token@domain/path
            url_without_protocol = self.git_remote_url[8:]  # Remove 'https://'
            return f"https://{self.git_username}:{self.git_pat}@{url_without_protocol}"
        else:
            # For SSH or other formats, return as-is
            return self.git_remote_url
            return self.git_remote_url
            
        # Handle different URL formats
        if self.git_remote_url.startswith('https://'):
            # For HTTPS URLs, embed credentials
            # Format: https://username:token@domain/path
            url_without_protocol = self.git_remote_url[8:]  # Remove 'https://'
            return f"https://{self.git_username}:{self.git_pat}@{url_without_protocol}"
        else:
            # For SSH or other formats, return as-is
            return self.git_remote_url

    def check_and_update_repo(self):
        """Check if there's already a git repository in the repo path and update it.
        
        If a repository exists, this method will:
        1. Check if the repo path contains a valid git repository
        2. Update the main repository to the latest state
        3. Update all submodules to their latest state
        
        Returns:
            bool: True if repository was found and updated, False if no repository exists
            
        Raises:
            git.exc.GitCommandError: If git operations fail
            Exception: If there are issues with repository operations
        """
        try:
            # Check if the repo path exists and contains a .git directory
            if not os.path.exists(self.git_repo_path):
                print(f"Repository path {self.git_repo_path} does not exist.")
                return False
                
            git_dir = os.path.join(self.git_repo_path, '.git')
            if not os.path.exists(git_dir):
                print(f"No git repository found at {self.git_repo_path}")
                return False
            
            print(f"Found existing git repository at {self.git_repo_path}")
            
            # Open the existing repository
            repo = git.Repo(self.git_repo_path)
            
            # Ensure we're not in a detached HEAD state
            if repo.head.is_detached:
                print("Repository is in detached HEAD state, checking out main/master branch")
                try:
                    repo.git.checkout('main')
                except git.exc.GitCommandError:
                    try:
                        repo.git.checkout('master')
                    except git.exc.GitCommandError:
                        print("Warning: Could not checkout main or master branch")
            
            # Set up authentication for the remote if credentials are provided
            if self.git_username and self.git_pat:
                # Update the remote URL to include authentication
                remote_url_with_auth = self._get_authenticated_remote_url()
                if 'origin' in [remote.name for remote in repo.remotes]:
                    repo.remotes.origin.set_url(remote_url_with_auth)
                    print("Updated remote origin URL with authentication")
            
            # Fetch the latest changes from the remote
            print("Fetching latest changes from remote...")
            repo.remotes.origin.fetch()
            
            # Pull the latest changes for the current branch
            current_branch = repo.active_branch.name
            print(f"Pulling latest changes for branch: {current_branch}")
            repo.remotes.origin.pull(current_branch)
            
            # Update submodules if they exist
            if repo.submodules:
                print(f"Found {len(repo.submodules)} submodules, updating them...")
                
                # Configure authentication for each submodule before updating
                for submodule in repo.submodules:
                    submodule_url = submodule.url
                    if submodule_url.startswith('https://') and self.git_username and self.git_pat:
                        # Add authentication to submodule URL
                        url_without_protocol = submodule_url[8:]  # Remove 'https://'
                        auth_submodule_url = f"https://{self.git_username}:{self.git_pat}@{url_without_protocol}"
                        repo.git.config(f'submodule.{submodule.name}.url', auth_submodule_url)
                        print(f"Configured authentication for submodule: {submodule.name}")
                
                # Update each submodule
                for submodule in repo.submodules:
                    print(f"Updating submodule: {submodule.name}")
                    submodule.update(init=True, recursive=True)
            else:
                print("No submodules found in the repository")
            
            print("Repository and all submodules updated successfully!")
            return True
            
        except git.exc.InvalidGitRepositoryError:
            print(f"Invalid git repository at {self.git_repo_path}")
            return False
        except git.exc.GitCommandError as e:
            print(f"Git command error: {e}")
            raise
        except Exception as e:
            print(f"Error updating repository: {e}")
            raise
    
    def clone_repo(self):
        """Clone the repository to the specified path.
        
        Returns:
            bool: True if repository was cloned successfully, False otherwise
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.git_repo_path), exist_ok=True)
            
            # Get authenticated URL for cloning
            auth_url = self._get_authenticated_remote_url()
            
            print(f"Cloning repository from {self.git_remote_url} to {self.git_repo_path}")
            
            # Clone the repository first (without recursive to handle auth manually)
            repo = git.Repo.clone_from(
                auth_url,
                self.git_repo_path,
                recursive=False  # We'll handle submodules manually with auth
            )
            
            # Handle submodules with authentication
            if repo.submodules:
                print(f"Found {len(repo.submodules)} submodules, setting up authentication...")
                
                # Initialize submodules
                repo.git.submodule('init')
                
                # Configure authentication for each submodule
                for submodule in repo.submodules:
                    submodule_url = submodule.url
                    if submodule_url.startswith('https://') and self.git_username and self.git_pat:
                        # Add authentication to submodule URL
                        url_without_protocol = submodule_url[8:]  # Remove 'https://'
                        auth_submodule_url = f"https://{self.git_username}:{self.git_pat}@{url_without_protocol}"
                        repo.git.config(f'submodule.{submodule.name}.url', auth_submodule_url)
                        print(f"Configured authentication for submodule: {submodule.name}")
                
                # Update submodules
                print("Updating submodules...")
                repo.git.submodule('update')
            
            print("Repository cloned successfully!")
            return True
            
        except git.exc.GitCommandError as e:
            print(f"Git command error during clone: {e}")
            return False
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return False
    
    def __repr__(self):
        """Return a string representation of the GitOperations instance.
        
        Returns:
            str: A string representation of the GitOperations.
        """
        return f"GitOperations(config={self.config}, git_repo_path='{self.git_repo_path}')"
