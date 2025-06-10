"""Basic tests for sync-icloud-git."""

def test_import():
    """Test that the package can be imported."""
    import sync_icloud_git
    # Basic import test - just verify the module exists
    assert hasattr(sync_icloud_git, '__name__')

def test_config_import():
    """Test that config module can be imported."""
    from sync_icloud_git.config import SyncConfig
    assert SyncConfig is not None

def test_git_operations_import():
    """Test that git_operations module can be imported."""
    from sync_icloud_git.git_operations import GitOperations
    assert GitOperations is not None
