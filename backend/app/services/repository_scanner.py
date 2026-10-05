from pathlib import Path

class RepositoryScanner:
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

        discovered_files = []

        def traverse(directory: Path) -> None:
            for entry in sorted(directory.iterdir()):
                if entry.is_symlink():
                    continue

                if entry.is_dir():
                    traverse(entry)
                elif entry.is_file():
                    relative_path = entry.relative_to(root)
                    discovered_files.append(
                        relative_path.as_posix()
                    )

        traverse(root)
        return discovered_files