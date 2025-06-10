"""Git operations module for sync-icloud-git."""
import os
import git


class GitOperations:
    """Class for handling Git operations with authentication support."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.git_remote_url = config.git_remote_url
        self.git_username = config.git_username
        self.git_pat = config.git_pat
        self.git_repo_path = config.git_repo_path
        self.repo = None
        
        if self.git_username and self.git_pat:
            print(f"Git authentication configured for user: {self.git_username}")


    def check_and_update_repo(self):
        """Check for existing repository and update it with submodules."""
        # Check if repository exists
        if not os.path.exists(self.git_repo_path) or not os.path.exists(os.path.join(self.git_repo_path, '.git')):
            return False
        
        try:
            print(f"Found existing git repository at {self.git_repo_path}")
            self.repo = git.Repo(self.git_repo_path)
            
            # Ensure we're on a proper branch
            if self.repo.head.is_detached:
                for branch in ['main', 'master']:
                    try:
                        self.repo.git.checkout(branch)
                        break
                    except git.exc.GitCommandError:
                        continue
            
            # Update remote URL with auth and fetch/pull
            if self.git_username and self.git_pat:
                self.repo.remotes.origin.set_url(self._get_auth_url())
            
            print("Fetching and pulling latest changes...")
            self.repo.remotes.origin.fetch()
            self.repo.remotes.origin.pull(self.repo.active_branch.name)

            # Update submodules
            self._setup_submodules()

            print("Repository and submodules updated successfully!")
            return True
            
        except Exception as e:
            print(f"Error updating repository: {e}")
            raise


    def clone_repo(self):
        """Clone repository with submodules."""
        try:
            os.makedirs(os.path.dirname(self.git_repo_path), exist_ok=True)
            print(f"Cloning repository from {self.git_remote_url} to {self.git_repo_path}")
            
            # Clone main repository
            self.repo = git.Repo.clone_from(self._get_auth_url(), self.git_repo_path, recursive=False)
            
            # Setup submodules
            self._setup_submodules()

            print("Repository cloned successfully!")
            return True
            
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return False


    def _get_auth_url(self, url=None):
        """Get URL with embedded authentication credentials."""
        target_url = url or self.git_remote_url
        if not self.git_username or not self.git_pat or not target_url.startswith('https://'):
            return target_url
        # Embed credentials: https://username:token@domain/path
        return f"https://{self.git_username}:{self.git_pat}@{target_url[8:]}"


    def _setup_submodules(self):
        """Setup and update submodules with authentication to latest commits."""
        if not self.repo.submodules:
            return

        print(f"Found {len(self.repo.submodules)} submodules, updating to latest...")

        # Configure auth and update submodules in one go
        for submodule in self.repo.submodules:
            if submodule.url.startswith('https://') and self.git_username and self.git_pat:
                self.repo.git.config(f'submodule.{submodule.name}.url', self._get_auth_url(submodule.url))

        # Init and update to latest commits from tracked branches
        self.repo.git.submodule('update', '--init', '--remote', '--recursive')


        # Ensure submodules are on proper branches (not detached HEAD)
        for submodule in self.repo.submodules:
            for branch in ['main', 'master']:
                try:
                    submodule.module().git.checkout(branch)
                    print(f"Updated submodule '{submodule.name}' on '{branch}'")
                    break
                except:
                    continue


    def __repr__(self):
        return f"GitOperations(git_repo_path='{self.git_repo_path}')"
