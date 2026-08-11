from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import zipfile


@dataclass
class LoadedTextFile:
    source_text: str
    content: str


@dataclass
class LoadStats:
    loaded_files: int = 0
    skipped_duplicates: int = 0
    skipped_invalid: int = 0


class FileLoader:
    """
    Finds and reads text files.

    Responsibilities:
    - scan folders recursively
    - read .txt files
    - read .txt files from a ZIP archive
    - validate that a file can be read as UTF-8 text
    - prevent the same physical/logical file from being loaded twice
    """

    def __init__(self) -> None:
        self._loaded_file_ids: set[str] = set()
        self.stats = LoadStats()

    def load(self, source: str | Path) -> list[LoadedTextFile]:
        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(f"Source does not exist: {source_path}")

        if source_path.is_dir():
            return self._load_directory(source_path)

        if source_path.is_file() and zipfile.is_zipfile(source_path):
            return self._load_zip(source_path)

        if source_path.is_file() and source_path.suffix.lower() == ".txt":
            loaded = self._load_txt_file(source_path, source_path.parent)
            return [loaded] if loaded is not None else []

        raise ValueError(
            "Source must be a directory, a .txt file, or a ZIP archive."
        )

    def _load_directory(self, root: Path) -> list[LoadedTextFile]:
        result: list[LoadedTextFile] = []

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() != ".txt":
                continue

            loaded = self._load_txt_file(file_path, root)
            if loaded is not None:
                result.append(loaded)

        return result

    def _load_txt_file(
        self,
        file_path: Path,
        root: Path,
    ) -> LoadedTextFile | None:
        file_id = str(file_path.resolve())

        if file_id in self._loaded_file_ids:
            self.stats.skipped_duplicates += 1
            return None

        try:
            content = file_path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            self.stats.skipped_invalid += 1
            return None

        self._loaded_file_ids.add(file_id)
        self.stats.loaded_files += 1

        try:
            source_text = str(file_path.relative_to(root))
        except ValueError:
            source_text = file_path.name

        return LoadedTextFile(
            source_text=source_text,
            content=content,
        )

    def _load_zip(self, archive_path: Path) -> list[LoadedTextFile]:
        result: list[LoadedTextFile] = []
        archive_id = str(archive_path.resolve())

        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                for member in archive.infolist():
                    if member.is_dir():
                        continue

                    member_path = PurePosixPath(member.filename)

                    if member_path.suffix.lower() != ".txt":
                        continue

                    file_id = f"{archive_id}::{member_path.as_posix()}"

                    if file_id in self._loaded_file_ids:
                        self.stats.skipped_duplicates += 1
                        continue

                    try:
                        raw = archive.read(member)
                        content = raw.decode("utf-8-sig")
                    except (OSError, UnicodeError, RuntimeError, zipfile.BadZipFile):
                        self.stats.skipped_invalid += 1
                        continue

                    self._loaded_file_ids.add(file_id)
                    self.stats.loaded_files += 1

                    result.append(
                        LoadedTextFile(
                            source_text=member_path.as_posix(),
                            content=content,
                        )
                    )
        except (OSError, zipfile.BadZipFile) as error:
            raise ValueError(f"Invalid ZIP archive: {archive_path}") from error

        return result
