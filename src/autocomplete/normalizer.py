import re
import unicodedata

from .models import WordPosition


def normalize_text(text: str) -> str:
    """
    Normalize text for search:
    - ignore upper/lower case
    - ignore punctuation
    - collapse repeated whitespace
    """
    text = text.lower()

    # Remove Unicode punctuation while keeping letters, digits and spaces.
    text = "".join(
        char
        for char in text
        if not unicodedata.category(char).startswith("P")
    )

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_word_positions(normalized_text: str) -> list[WordPosition]:
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

    return positions
