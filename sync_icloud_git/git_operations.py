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
        
        if self.git_username and self.git_pat and config.verbose:
            print(f"Git authentication configured for user: {self.git_username}")


    def load_existing_repo(self):
        """Load an existing repository without updating it."""
        if not os.path.exists(self.git_repo_path) or not os.path.exists(os.path.join(self.git_repo_path, '.git')):
            return False
        
        try:
            print(f"Loading existing git repository at {self.git_repo_path}")
            self.repo = git.Repo(self.git_repo_path)
            # Configure git identity for commits
            self._configure_git_identity(self.repo)
            return True
        except Exception as e:
            print(f"Error loading repository: {e}")
            return False


    def check_and_update_repo(self):
        """Check for existing repository and update it with submodules."""
        # Check if repository exists
        if not os.path.exists(self.git_repo_path) or not os.path.exists(os.path.join(self.git_repo_path, '.git')):
            return False
        
        try:
            print(f"Found existing git repository at {self.git_repo_path}")
            self.repo = git.Repo(self.git_repo_path)
            
            # Configure git identity for commits
            self._configure_git_identity(self.repo)
            
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
            
            # Configure git identity for commits
            self._configure_git_identity(self.repo)
            
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

    def _configure_git_identity(self, repo):
        """Configure git user identity for commits."""
        try:
            # Set git user.name and user.email for this repository
            repo.git.config('user.name', self.config.git_commit_username)
            repo.git.config('user.email', self.config.git_commit_email)
            
            if self.config.verbose:
                print(f"Git identity configured: {self.config.git_commit_username} <{self.config.git_commit_email}>")
        except Exception as e:
            print(f"Warning: Could not configure git identity: {e}")
            # Don't fail the operation, just warn


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
                    submodule_repo = submodule.module()
                    submodule_repo.git.checkout(branch)
                    # Configure git identity for submodule commits
                    self._configure_git_identity(submodule_repo)
                    print(f"Updated submodule '{submodule.name}' on '{branch}'")
                    break
                except:
                    continue


    def commit_changes(self):
        """Commit all changes in the main repository and submodules."""
        if not self.repo:
            print("No repository loaded. Cannot commit changes.")
            return False
        
        try:
            commit_message = self.config.git_commit_message
            committed_repos = []
            
            # First, commit changes in all submodules
            for submodule in self.repo.submodules:
                try:
                    submodule_repo = submodule.module()
                    
                    # Check if there are changes to commit in the submodule
                    if submodule_repo.is_dirty(untracked_files=True):
                        print(f"Committing changes in submodule: {submodule.name}")
                        
                        # Add all changes (including untracked files)
                        submodule_repo.git.add('-A')
                        
                        # Commit the changes
                        submodule_repo.index.commit(commit_message)
                        committed_repos.append(f"submodule '{submodule.name}'")
                        
                        print(f"Successfully committed changes in submodule: {submodule.name}")
                    else:
                        print(f"No changes to commit in submodule: {submodule.name}")
                        
                except Exception as e:
                    print(f"Error committing changes in submodule {submodule.name}: {e}")
                    continue
            
            # Then, commit changes in the main repository (including submodule updates)
            if self.repo.is_dirty(untracked_files=True):
                print("Committing changes in main repository...")
                
                # Add all changes (including untracked files and submodule updates)
                self.repo.git.add('-A')
                
                # Commit the changes
                self.repo.index.commit(commit_message)
                committed_repos.append("main repository")
                
                print("Successfully committed changes in main repository")
            else:
                print("No changes to commit in main repository")
            
            if committed_repos:
                print(f"Changes committed successfully in: {', '.join(committed_repos)}")
                print(f"Commit message used: '{commit_message}'")
                return True
            else:
                print("No changes found to commit in any repository")
                return False
                
        except Exception as e:
            print(f"Error committing changes: {e}")
            return False


    def push_changes(self):
        """Push committed changes to remote repositories."""
        if not self.repo:
            print("No repository loaded. Cannot push changes.")
            return False
        
        try:
            pushed_repos = []
            
            # First, push changes in all submodules
            for submodule in self.repo.submodules:
                try:
                    submodule_repo = submodule.module()
                    
                    # Check if there are commits to push
                    if list(submodule_repo.iter_commits('HEAD@{u}..HEAD')):
                        print(f"Pushing changes in submodule: {submodule.name}")
                        
                        # Push to the remote
                        origin = submodule_repo.remote('origin')
                        origin.push()
                        pushed_repos.append(f"submodule '{submodule.name}'")
                        
                        print(f"Successfully pushed changes in submodule: {submodule.name}")
                    else:
                        print(f"No commits to push in submodule: {submodule.name}")
                        
                except Exception as e:
                    print(f"Error pushing changes in submodule {submodule.name}: {e}")
                    continue
            
            # Then, push changes in the main repository
            if list(self.repo.iter_commits('HEAD@{u}..HEAD')):
                print("Pushing changes in main repository...")
                
                # Push to the remote
                origin = self.repo.remote('origin')
                origin.push()
                pushed_repos.append("main repository")
                
                print("Successfully pushed changes in main repository")
            else:
                print("No commits to push in main repository")
            
            if pushed_repos:
                print(f"Changes pushed successfully to: {', '.join(pushed_repos)}")
                return True
            else:
                print("No changes found to push in any repository")
                return False
                
        except Exception as e:
            print(f"Error pushing changes: {e}")
            return False


    def _print_repo_changes(self, repo):
        """Print git status for a repository."""
        try:
            # Use git status --porcelain for clean, parseable output
            status_output = repo.git.status('--porcelain')
            if status_output.strip():
                print(status_output)
            else:
                print("  (no changes)")
        except Exception as e:
            print(f"  Error getting status: {e}")

    def show_changed_files(self):
        """Show files that have changed since the last commit in main repo and submodules."""
        if not self.repo:
            print("No repository loaded.")
            return False
        
        # Main repository
        print(f"Main repository ({self.git_repo_path}):")
        self._print_repo_changes(self.repo)
        
        # Submodules
        for submodule in self.repo.submodules:
            try:
                submodule_repo = submodule.module()
                print(f"Submodule '{submodule.name}':")
                self._print_repo_changes(submodule_repo)
            except Exception as e:
                print(f"Submodule '{submodule.name}': Error - {e}")
        
        return True

    def __repr__(self):
        return f"GitOperations(git_repo_path='{self.git_repo_path}')"
