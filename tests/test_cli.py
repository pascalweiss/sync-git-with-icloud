"""Tests for CLI exit codes."""

import pytest

pytest.importorskip("git")
pytest.importorskip("rclone_python")

from sync_icloud_git.config import SyncConfig
import sync_icloud_git.cli as cli


@pytest.fixture
def mock_dependencies(monkeypatch, tmp_path):
    """Provide minimal stubs for CLI dependencies."""

    config = SyncConfig(
        git_remote_url="https://example.com/repo.git",
        git_username="user",
        git_pat="token",
        git_repo_path=str(tmp_path / "repo"),
        git_commit_message="Sync",
        rclone_config_content="[remote]\n",
        rclone_remote_folder="Documents/Test",
        verbose=False,
    )

    class DummyGitOperations:
        def __init__(self, cfg):
            self.config = cfg

    class DummyICloudOperations:
        def __init__(self, cfg):
            self.config = cfg

    monkeypatch.setattr(cli, "GitOperations", DummyGitOperations)
    monkeypatch.setattr(cli, "ICloudOperations", DummyICloudOperations)
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
