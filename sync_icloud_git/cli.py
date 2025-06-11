"""Command line interface for sync-icloud-git."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from sync_icloud_git.config import SyncConfig
from sync_icloud_git.git_operations import GitOperations
from sync_icloud_git.icloud_operations import ICloudOperations


class Step(ABC):
    """Abstract base class for pipeline steps."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the step. Returns True if successful."""
        pass


class RepositoryUpdateStep(Step):
    @property
    def name(self) -> str:
        return "Checking for existing git repository"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        git_ops = context['git_ops']
        config = context['config']
        
        print(f"\n--- {self.name} ---")
        repo_updated = git_ops.check_and_update_repo()
        
        if repo_updated:
            print("✅ Repository update completed successfully!")
            context['repo_updated'] = True
            return True
        else:
            context['repo_updated'] = False
            if config.step == 'all':
                print("ℹ️  No existing repository found at the specified path.")
                return True
            else:
                print("ℹ️  No existing repository found. Use --step=clone or --step=all to clone first.")
                return False


class RepositoryLoadStep(Step):
    @property
    def name(self) -> str:
        return "Loading existing repository"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        git_ops = context['git_ops']
        
        print(f"\n--- {self.name} ---")
        repo_loaded = git_ops.load_existing_repo()
        
        if repo_loaded:
            print("✅ Repository loaded successfully!")
            return True
        else:
            print("❌ Failed to load repository. Repository may not exist.")
            return False


class RepositoryCloneStep(Step):
    @property
    def name(self) -> str:
        return "Cloning repository"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        git_ops = context['git_ops']
        config = context['config']
        
        # Only run if we're doing 'all' and update failed, or if we're doing 'clone'
        if config.step == 'all' and context.get('repo_updated', False):
            return True  # Skip cloning if update was successful
        
        print(f"\n--- {self.name} ---")
        clone_success = git_ops.clone_repo()
        
        if clone_success:
            print("✅ Repository cloned successfully!")
            return True
        else:
            print("❌ Failed to clone repository.")
            return False


class ICloudSyncStep(Step):
    @property
    def name(self) -> str:
        return "Syncing from iCloud"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        icloud_ops = context['icloud_ops']
        
        print(f"\n--- {self.name} ---")
        try:
            icloud_ops.sync_from_icloud_to_repo()
            print("✅ iCloud sync completed successfully!")
            return True
        except Exception as e:
            print(f"❌ iCloud sync failed: {e}")
            return False


class ShowChangesStep(Step):
    @property
    def name(self) -> str:
        return "Files changed after sync"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        git_ops = context['git_ops']
        
        print(f"\n--- {self.name} ---")
        git_ops.show_changed_files()
        return True


class CommitStep(Step):
    @property
    def name(self) -> str:
        return "Committing changes"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        git_ops = context['git_ops']
        
        print(f"\n--- {self.name} ---")
        try:
            commit_success = git_ops.commit_changes()
            if commit_success:
                print("✅ Changes committed successfully!")
            else:
                print("ℹ️  No changes to commit.")
            return True
        except Exception as e:
            print(f"❌ Failed to commit changes: {e}")
            return False


class PushStep(Step):
    @property
    def name(self) -> str:
        return "Pushing changes to remote"
    
    def execute(self, context: Dict[str, Any]) -> bool:
        git_ops = context['git_ops']
        
        print(f"\n--- {self.name} ---")
        try:
            push_success = git_ops.push_changes()
            if push_success:
                print("✅ Changes pushed to remote successfully!")
            else:
                print("ℹ️  No changes to push.")
            return True
        except Exception as e:
            print(f"❌ Failed to push changes: {e}")
            return False


class StepPipeline:
    """Manages execution of steps based on configuration."""
    
    def __init__(self):
        self.step_definitions = {
            'all': [
                RepositoryUpdateStep(),
                RepositoryCloneStep(),
                ICloudSyncStep(),
                ShowChangesStep(),
                CommitStep(),
                PushStep()
            ],
            'update': [RepositoryUpdateStep()],
            'clone': [RepositoryCloneStep()],
            'sync': [
                RepositoryLoadStep(),
                ICloudSyncStep(),
                ShowChangesStep(),
                CommitStep(),
                PushStep()
            ]
        }
    
    def execute(self, config, git_ops, icloud_ops) -> bool:
        """Execute the pipeline for the given step."""
        context = {
            'config': config,
            'git_ops': git_ops,
            'icloud_ops': icloud_ops
        }
        
        steps = self.step_definitions.get(config.step, [])
        
        for step in steps:
            success = step.execute(context)
            if not success:
                return False
        
        return True


def main():
    """Run the main program."""
    config = SyncConfig.load_config()
    
    # Only print configuration details if verbose mode is enabled
    if config.verbose:
        print(f"Configuration: {config}")
    
    # Create an instance of GitOperations with the loaded configuration
    git_ops = GitOperations(config)
    if config.verbose:
        print(f"GitOperations: {git_ops}")
    
    # Create an instance of ICloudOperations with the loaded configuration
    icloud_ops = ICloudOperations(config)
    if config.verbose:
        print(f"ICloudOperations: {icloud_ops}")
    
    # Execute the pipeline based on the step parameter
    pipeline = StepPipeline()
    success = pipeline.execute(config, git_ops, icloud_ops)
    
    if success:
        print("\n🎉 Sync operation completed successfully!")
    else:
        print("\n❌ Sync operation failed!")


if __name__ == "__main__":
    main()
