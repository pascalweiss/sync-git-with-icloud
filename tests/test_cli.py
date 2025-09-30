"""Tests for CLI exit codes."""
from types import SimpleNamespace

import pytest

pytest.importorskip("git")
pytest.importorskip("rclone_python")

import sync_icloud_git.cli as cli


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
