from enum import Enum


class EditType(Enum):
    """Correction required to turn the user query into target text.

    INSERTION means inserting a missing character into the query (for
    example, ``pyton`` -> ``python``). DELETION means deleting an extra
    character from the query (for example, ``pythhon`` -> ``python``).
    """

    EXACT = "exact"
    REPLACEMENT = "replacement"
    INSERTION = "insertion"
    DELETION = "deletion"
