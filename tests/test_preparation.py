from pathlib import Path
import zipfile

from autocomplete import DataPreparer
from autocomplete.normalizer import get_word_positions, normalize_text


def test_normalize_text():
    assert normalize_text("Hello,   WORLD!!!") == "hello world"


def test_word_positions():
    positions = get_word_positions("this is a test")

    assert [item.word for item in positions] == ["this", "is", "a", "test"]
    assert [(item.start, item.end) for item in positions] == [
        (0, 4),
        (5, 7),
        (8, 9),
        (10, 14),
    ]


def test_prepare_directory_and_offsets(tmp_path: Path):
    source = tmp_path / "data"
    source.mkdir()

    text_file = source / "sample.txt"
    text_file.write_text(
        "First sentence.\n\nSecond sentence!\n",
        encoding="utf-8",
    )

    preparer = DataPreparer()
    result = preparer.prepare(source)

    assert len(result) == 2
    assert result[0].normalized_sentence == "first sentence"
    assert result[0].offset == 1
    assert result[1].normalized_sentence == "second sentence"
    assert result[1].offset == 3


def test_same_file_is_not_loaded_twice(tmp_path: Path):
    text_file = tmp_path / "sample.txt"
    text_file.write_text("Hello world\n", encoding="utf-8")

    preparer = DataPreparer()

    first = preparer.prepare(text_file)
    second = preparer.prepare(text_file)

    assert len(first) == 1
    assert second == []
    assert preparer.loader.stats.skipped_duplicates == 1


def test_prepare_zip(tmp_path: Path):
    archive_path = tmp_path / "Archive.zip"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "folder/a.txt",
            "Hello, WORLD!\nAnother   line.\n",
        )
        archive.writestr("ignore.bin", b"123")

    preparer = DataPreparer()
    result = preparer.prepare(archive_path)

    assert len(result) == 2
    assert result[0].source_text == "folder/a.txt"
    assert result[0].normalized_sentence == "hello world"
    assert result[1].offset == 2
