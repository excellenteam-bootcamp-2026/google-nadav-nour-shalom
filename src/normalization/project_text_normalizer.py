import re
import string
import unicodedata

from src.contracts.text_normalizer import TextNormalizer


class _PunctuationTable(dict):
    """``str.translate`` mapping that deletes every punctuation character.

    ``string.punctuation`` is ASCII-only, which would leave curly quotes,
    dashes, ellipses and Hebrew punctuation (maqaf, geresh, gershayim) in
    the normalized text. The specification says the user never has to type
    punctuation, so Unicode punctuation is stripped as well. The ASCII set
    is still consulted because it contains symbols such as ``$`` and ``+``
    that Unicode classifies as ``S``, not ``P``.

    Verdicts are computed per code point on first sight and cached, rather
    than by walking the whole Unicode range up front.
    """

    def __missing__(self, code_point: int) -> str | None:
        character = chr(code_point)
        is_punctuation = (
            character in string.punctuation
            or unicodedata.category(character).startswith("P")
        )
        verdict = None if is_punctuation else character
        self[code_point] = verdict
        return verdict


class ProjectTextNormalizer(TextNormalizer):
    """Apply the project's predictable English normalization rules."""

    _punctuation_table = _PunctuationTable()

    def normalize(self, text: str) -> str:
        text = text.lower()

        text = text.translate(self._punctuation_table)

        text = re.sub(r"\s+", " ", text)

        return text.strip()
