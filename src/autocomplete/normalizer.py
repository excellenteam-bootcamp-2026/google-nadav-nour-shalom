import re

from src.models.word_position import WordPosition
from src.normalization.project_text_normalizer import ProjectTextNormalizer


_project_normalizer = ProjectTextNormalizer()


def normalize_text(text: str) -> str:
    """Normalize with the same concrete implementation used online."""
    return _project_normalizer.normalize(text)


def get_word_positions(normalized_text: str) -> tuple[WordPosition, ...]:
    """
    Return each word and its character range in the normalized sentence.
    'end' is exclusive.
    """
    positions: list[WordPosition] = []

    for match in re.finditer(r"\S+", normalized_text):
        positions.append(
            WordPosition(
                word=match.group(),
                start=match.start(),
                end=match.end(),
            )
        )

    return tuple(positions)
