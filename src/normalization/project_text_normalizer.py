import re
import string

from src.contracts.text_normalizer import TextNormalizer


class ProjectTextNormalizer(TextNormalizer):
    """Apply the project's predictable English normalization rules."""

    _punctuation_table = str.maketrans(
        "",
        "",
        string.punctuation,
    )

    def normalize(self, text: str) -> str:
        text = text.lower()

        text = text.translate(self._punctuation_table)

        text = re.sub(r"\s+", " ", text)

        return text.strip()
