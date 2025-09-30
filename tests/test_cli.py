"""Tests for CLI exit codes."""
import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

# Ensure the base package loads so we can stub submodules
import sync_icloud_git  # noqa: F401  # Import to register package


def _install_stub_modules():
    """Install lightweight stubs for heavy dependency modules."""

    if 'sync_icloud_git.git_operations' not in sys.modules:
        git_ops_module = ModuleType('sync_icloud_git.git_operations')

        class DummyGitOperations:
            def __init__(self, config):
                self.config = config

        git_ops_module.GitOperations = DummyGitOperations
        sys.modules['sync_icloud_git.git_operations'] = git_ops_module

    if 'sync_icloud_git.icloud_operations' not in sys.modules:
        icloud_module = ModuleType('sync_icloud_git.icloud_operations')

        class DummyICloudOperations:
            def __init__(self, config):
                self.config = config

        icloud_module.ICloudOperations = DummyICloudOperations
        sys.modules['sync_icloud_git.icloud_operations'] = icloud_module


_install_stub_modules()
cli = importlib.import_module('sync_icloud_git.cli')


@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mock heavy dependencies used by the CLI entry point."""

    # Minimal config object consumed by the CLI
    config = SimpleNamespace(verbose=False)

    monkeypatch.setattr(cli.SyncConfig, "load_config", lambda: config)

    return config


def test_main_exits_zero_on_success(monkeypatch, mock_dependencies):
    """CLI should exit with code 0 when the pipeline succeeds."""

    monkeypatch.setattr(
        cli.StepPipeline,
        "execute",
        lambda self, cfg, git_ops, icloud_ops: True,
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 0


def test_main_exits_one_on_failure(monkeypatch, mock_dependencies):
    """CLI should exit with code 1 when the pipeline fails."""

    monkeypatch.setattr(
        cli.StepPipeline,
        "execute",
        lambda self, cfg, git_ops, icloud_ops: False,
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 1
