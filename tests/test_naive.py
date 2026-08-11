import unittest

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.contracts.search_algorithm import SearchAlgorithm
from src.models.edit_type import EditType
from src.models.prepared_sentence import PreparedSentence
from src.normalization.project_text_normalizer import ProjectTextNormalizer


class NaiveSearchAlgorithmTests(unittest.TestCase):
    def setUp(self) -> None:
        self.algorithm = NaiveSearchAlgorithm()

    @staticmethod
    def _sentence(
        normalized_text: str,
        *,
        original_text: str | None = None,
        sentence_id: int = 1,
        source_path: str = "archive/example.txt",
        offset: int = 7,
    ) -> PreparedSentence:
        return PreparedSentence(
            sentence_id=sentence_id,
            original_text=(
                normalized_text if original_text is None else original_text
            ),
            normalized_text=normalized_text,
            source_path=source_path,
            offset=offset,
        )

    def _search(self, query: str, target: str):
        self.algorithm.build([self._sentence(target)])
        return self.algorithm.search(query)

    @staticmethod
    def _matching(
        candidates,
        edit_type: EditType,
        *,
        match_start: int = 0,
    ):
        return [
            candidate
            for candidate in candidates
            if candidate.edit_type is edit_type
            and candidate.match_start == match_start
        ]

    def test_exact_match_has_no_edit_index(self) -> None:
        matches = self._matching(
            self._search("python", "python"),
            EditType.EXACT,
        )

        self.assertEqual(1, len(matches))
        self.assertIsNone(matches[0].edit_index)
        self.assertEqual(6, matches[0].correct_characters)

    def test_replacement_reports_query_character_index(self) -> None:
        matches = self._matching(
            self._search("pythom", "python"),
            EditType.REPLACEMENT,
        )

        self.assertEqual([5], [match.edit_index for match in matches])

    def test_insertion_in_middle_reports_query_slot(self) -> None:
        matches = self._matching(
            self._search("pyton", "python"),
            EditType.INSERTION,
        )

        self.assertEqual([3], [match.edit_index for match in matches])

    def test_insertion_at_beginning_reports_slot_zero(self) -> None:
        matches = self._matching(
            self._search("ython", "python"),
            EditType.INSERTION,
        )

        self.assertEqual([0], [match.edit_index for match in matches])

    def test_insertion_at_end_reports_query_length(self) -> None:
        matches = self._matching(
            self._search("pytho", "python"),
            EditType.INSERTION,
        )

        self.assertEqual([5], [match.edit_index for match in matches])

    def test_repeated_middle_character_exposes_both_deletions(self) -> None:
        matches = self._matching(
            self._search("pythhon", "python"),
            EditType.DELETION,
        )

        self.assertEqual({3, 4}, {match.edit_index for match in matches})

    def test_deletion_at_beginning_reports_index_zero(self) -> None:
        matches = self._matching(
            self._search("xpython", "python"),
            EditType.DELETION,
        )

        self.assertEqual([0], [match.edit_index for match in matches])

    def test_repeated_final_character_includes_final_query_index(self) -> None:
        matches = self._matching(
            self._search("pythonn", "python"),
            EditType.DELETION,
        )

        self.assertEqual({5, 6}, {match.edit_index for match in matches})
        self.assertIn(6, {match.edit_index for match in matches})

    def test_more_than_one_edit_is_rejected(self) -> None:
        self.assertEqual([], self._search("pyxxom", "python"))

    def test_exact_match_can_start_in_middle_of_word(self) -> None:
        matches = self._matching(
            self._search("gramm", "i love programming"),
            EditType.EXACT,
            match_start=10,
        )

        self.assertEqual(1, len(matches))

    def test_exact_match_can_cross_word_boundary(self) -> None:
        matches = self._matching(
            self._search("lo wo", "hello world"),
            EditType.EXACT,
            match_start=3,
        )

        self.assertEqual(1, len(matches))

    def test_overlapping_exact_occurrences_are_all_returned(self) -> None:
        matches = [
            match
            for match in self._search("aa", "aaa")
            if match.edit_type is EditType.EXACT
        ]

        self.assertEqual([0, 1], [match.match_start for match in matches])

    def test_empty_query_returns_no_candidates(self) -> None:
        self.algorithm.build([self._sentence("anything")])

        self.assertEqual([], self.algorithm.search(""))

    def test_one_character_query_never_matches_empty_target(self) -> None:
        self.algorithm.build([self._sentence("")])

        self.assertEqual([], self.algorithm.search("a"))

    def test_repeated_character_insertion_exposes_every_valid_slot(self) -> None:
        matches = self._matching(
            self._search("aa", "aaa"),
            EditType.INSERTION,
        )

        self.assertEqual({0, 1, 2}, {match.edit_index for match in matches})

    def test_repeated_character_deletion_exposes_every_valid_index(self) -> None:
        matches = self._matching(
            self._search("aaa", "aa"),
            EditType.DELETION,
        )

        self.assertEqual({0, 1, 2}, {match.edit_index for match in matches})

    def test_candidate_resolves_original_sentence_metadata(self) -> None:
        sentence = self._sentence(
            "hello world",
            original_text="  Hello,   WORLD!  ",
            sentence_id=42,
            source_path="archive/nested/source.txt",
            offset=19,
        )
        self.algorithm.build([sentence])

        match = self._matching(
            self.algorithm.search("hello world"),
            EditType.EXACT,
        )[0]

        self.assertIs(sentence, match.sentence)
        self.assertEqual("  Hello,   WORLD!  ", match.sentence.original_text)
        self.assertEqual("hello world", match.sentence.normalized_text)
        self.assertEqual("archive/nested/source.txt", match.sentence.source_path)
        self.assertEqual(19, match.sentence.offset)

    def test_search_contract_has_only_generic_abstract_operations(self) -> None:
        self.assertEqual(
            frozenset({"build", "search"}),
            SearchAlgorithm.__abstractmethods__,
        )


class ProjectTextNormalizerTests(unittest.TestCase):
    def test_normalization_ignores_case_punctuation_and_extra_space(self) -> None:
        normalizer = ProjectTextNormalizer()

        self.assertEqual(
            "hello world",
            normalizer.normalize("  Hello,   WORLD!  "),
        )

    def test_normalization_uses_lower_without_unicode_expansion(self) -> None:
        normalizer = ProjectTextNormalizer()

        self.assertEqual("straße", normalizer.normalize("Straße"))


if __name__ == "__main__":
    unittest.main()
