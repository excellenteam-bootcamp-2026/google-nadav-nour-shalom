from pathlib import Path
import shutil
import unittest
import zipfile

from src.autocomplete import DataPreparer
from src.autocomplete.models import PreparedSentence
from src.autocomplete.normalizer import get_word_positions, normalize_text
from src.models.prepared_sentence import PreparedSentence as SharedSentence


class DataPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = Path.cwd() / "tests" / "_runtime"
        if self.temporary_directory.exists():
            shutil.rmtree(self.temporary_directory)
        self.temporary_directory.mkdir()

    def tearDown(self) -> None:
        if self.temporary_directory.exists():
            shutil.rmtree(self.temporary_directory)

    def test_normalize_text_uses_shared_project_semantics(self) -> None:
        self.assertEqual("hello world", normalize_text("Hello,   WORLD!!!"))

    def test_word_positions(self) -> None:
        positions = get_word_positions("this is a test")

        self.assertEqual(
            ["this", "is", "a", "test"],
            [item.word for item in positions],
        )
        self.assertEqual(
            [(0, 4), (5, 7), (8, 9), (10, 14)],
            [(item.start, item.end) for item in positions],
        )

    def test_prepare_directory_preserves_text_and_one_based_offsets(self) -> None:
        source = self.temporary_directory / "data"
        source.mkdir()
        (source / "sample.txt").write_text(
            "  First sentence.  \n\nSecond sentence!\n",
            encoding="utf-8",
        )

        result = DataPreparer().prepare(source)

        self.assertEqual(2, len(result))
        self.assertIs(PreparedSentence, SharedSentence)
        self.assertIsInstance(result[0], SharedSentence)
        self.assertEqual(0, result[0].sentence_id)
        self.assertEqual("  First sentence.  ", result[0].original_text)
        self.assertEqual("first sentence", result[0].normalized_text)
        self.assertEqual("sample.txt", result[0].source_path)
        self.assertEqual(1, result[0].offset)
        self.assertEqual(3, result[1].offset)

    def test_same_file_is_not_loaded_twice(self) -> None:
        text_file = self.temporary_directory / "sample.txt"
        text_file.write_text("Hello world\n", encoding="utf-8")
        preparer = DataPreparer()

        first = preparer.prepare(text_file)
        second = preparer.prepare(text_file)

        self.assertEqual(1, len(first))
        self.assertEqual([], second)
        self.assertEqual(1, preparer.loader.stats.skipped_duplicates)

    def test_prepare_zip(self) -> None:
        archive_path = self.temporary_directory / "Archive.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(
                "folder/a.txt",
                "Hello, WORLD!\nAnother   line.\n",
            )
            archive.writestr("ignore.bin", b"123")

        result = DataPreparer().prepare(archive_path)

        self.assertEqual(2, len(result))
        self.assertEqual("folder/a.txt", result[0].source_path)
        self.assertEqual("hello world", result[0].normalized_text)
        self.assertEqual(2, result[1].offset)


if __name__ == "__main__":
    unittest.main()
