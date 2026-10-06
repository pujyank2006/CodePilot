from pathlib import Path
from pathspec import PathSpec

DEFAULT_IGNORES = [
    ".git/",
    "node_modules/",
    ".venv/",
    "venv/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "dist/",
    "build/",
    ".next/",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
    ".gitignore"
]

class RepositoryScanner:
    def __init__(self):
        self.ignore_spec = PathSpec.from_lines(
            "gitwildmatch",
            DEFAULT_IGNORES
        )

    def _load_ignore_spec(self, root: Path) -> PathSpec:
        patterns = list(DEFAULT_IGNORES)
        gitignore = root / ".gitignore"

        if gitignore.is_file():
            patterns.extend(
                gitignore.read_text(
                    encoding = "utf-8",
                    errors = "replace"
                ).splitlines()
            )

        return PathSpec.from_lines("gitwildmatch", patterns)

    def _is_ignored(
            self,
            relative_path: str,
            is_directory: bool,
            ignore_spec: PathSpec,
    ) -> bool:
        path = relative_path + "/" if is_directory else relative_path
        return ignore_spec.match_file(path)

    @staticmethod
    def _is_binary_file(path: Path) -> bool:
        try:
            with path.open("rb") as file:
                sample = file.read(8192)
            return b"\0" in sample
        except OSError:
            return True
    
    def scan(self, repository_path: str | Path) -> list[str]:
        root = Path(repository_path).resolve()

        if not root.exists():
            raise FileNotFoundError(
                f"Repository path does not exists: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {root}"
            )

        ignore_spec = self._load_ignore_spec(root)
        discovered_files = []

        def traverse(directory: Path) -> None:
            for entry in sorted(directory.iterdir()):
                if entry.is_symlink():
                    continue

                relative_path = entry.relative_to(root).as_posix()
                is_directory = entry.is_dir()

                if self._is_ignored(
                    relative_path,
                    is_directory,
                    ignore_spec
                ):
                    continue

                if is_directory:
                    traverse(entry)
                elif entry.is_file():
                    if self._is_binary_file(entry):
                        continue

                    discovered_files.append(relative_path)
    
        traverse(root)
        return discovered_files