
from pathlib import Path

import pytest

from app.services.repository_scanner import RepositoryScanner


@pytest.fixture
def scanner():
    return RepositoryScanner()


def test_scans_nested_files(scanner, tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "routes.py").write_text("def home(): pass")

    result = scanner.scan(tmp_path)

    assert "main.py" in result
    assert "app/routes.py" in result


def test_ignores_default_directories(scanner, tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")

    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "package.js").write_text("module.exports = {}")

    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "python.py").write_text("# environment file")

    result = scanner.scan(tmp_path)

    assert "main.py" in result
    assert "node_modules/package.js" not in result
    assert ".venv/python.py" not in result


def test_respects_gitignore(scanner, tmp_path):
    (tmp_path / ".gitignore").write_text(
        "private/\n*.log\n"
    )
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "debug.log").write_text("log data")

    private_dir = tmp_path / "private"
    private_dir.mkdir()
    (private_dir / "notes.txt").write_text("private data")

    result = scanner.scan(tmp_path)

    assert "main.py" in result
    assert "debug.log" not in result
    assert "private/notes.txt" not in result


def test_ignores_secrets_and_binary_files(scanner, tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / ".env").write_text("API_KEY=secret")
    (tmp_path / "private.key").write_text("private key")

    (tmp_path / "image.png").write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00"
    )

    result = scanner.scan(tmp_path)

    assert "main.py" in result
    assert ".env" not in result
    assert "private.key" not in result
    assert "image.png" not in result


def test_rejects_nonexistent_repository(scanner, tmp_path):
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        scanner.scan(missing)


def test_rejects_file_as_repository(scanner, tmp_path):
    file_path = tmp_path / "main.py"
    file_path.write_text("print('hello')")

    with pytest.raises(NotADirectoryError):
        scanner.scan(file_path)