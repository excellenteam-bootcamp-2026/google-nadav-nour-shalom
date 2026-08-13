"""Binary cache for the Bi-Anchor search index.

Provides memory-efficient build, save, and load of the complete Bi-Anchor
search index.  Uses array.array('i') throughout — each int occupies 4 bytes
of contiguous C memory instead of 28 bytes as a Python int object — keeping
total memory under ~500 MB even for the full 32 MB corpus.

Cache file layout
-----------------
    Header      :  magic (4 B) + version/q/counts (16 B)
    Sentences   :  all PreparedSentence fields (strings + ints)
    Words       :  unique word strings
    Word index  :  word_id -> array of (sentence_id, word_start) pairs
    Intra seeds :  seed_str -> array of (word_id, offset) pairs
    Boundary    :  seed_str -> array of (sentence_id, position) pairs

All int arrays are written with array.tobytes() and read with
array.frombytes(), giving zero-copy speed and no Python-object overhead.
"""

from __future__ import annotations

import hashlib
import struct
import time
from array import array
from pathlib import Path
from re import finditer

from src.cache.cached_seed_lookup import CachedSeedLookup
from src.models.prepared_sentence import PreparedSentence

CACHE_MAGIC = b"BIAC"
CACHE_VERSION = 1


# ------------------------------------------------------------------
# Low-level binary I/O helpers
# ------------------------------------------------------------------

def _write_str(f, s: str) -> None:
    data = s.encode("utf-8")
    f.write(struct.pack("<I", len(data)))
    f.write(data)


def _read_str(f) -> str:
    (n,) = struct.unpack("<I", f.read(4))
    return f.read(n).decode("utf-8")


def _write_array(f, arr: array) -> None:
    f.write(struct.pack("<I", len(arr)))
    f.write(arr.tobytes())


def _read_array(f) -> array:
    (n,) = struct.unpack("<I", f.read(4))
    arr = array("i")
    if n > 0:
        arr.frombytes(f.read(n * 4))
    return arr


# ------------------------------------------------------------------
# Source fingerprinting (cache invalidation)
# ------------------------------------------------------------------

def source_fingerprint(source: Path) -> str:
    """Hash based on the source file's name, size and modification time."""
    stat = source.stat()
    raw = f"{source.name}:{stat.st_size}:{stat.st_mtime}"
    return hashlib.md5(raw.encode()).hexdigest()


def cache_is_valid(source: Path, cache_path: Path, fp_path: Path) -> bool:
    """Return True when the cache matches the current source archive."""
    if not cache_path.exists() or not fp_path.exists():
        return False
    stored = fp_path.read_text(encoding="utf-8").strip()
    return stored == source_fingerprint(source)


# ------------------------------------------------------------------
# Build + Save  (runs once per unique source archive)
# ------------------------------------------------------------------

def build_and_save(
    sentences: list[PreparedSentence],
    output_path: Path,
    q: int = 3,
) -> CachedSeedLookup:
    """Build the Bi-Anchor index and write it to a binary cache file.

    Uses array.array('i') everywhere to avoid creating millions of Python
    objects.  Returns a CachedSeedLookup ready for immediate search.
    """
    t0 = time.time()
    total = len(sentences)
    print(f"Building Bi-Anchor index ({total:,} sentences, q={q})...")

    # -- 1. Extract words and record their positions --------------------
    word_ids: dict[str, int] = {}
    unique_words: list[str] = []
    word_occ: dict[int, array] = {}           # wid -> [sid, start, ...]

    for i, sentence in enumerate(sentences):
        if i > 0 and i % 500_000 == 0:
            print(f"  Word extraction: {i:,} / {total:,}")
        for match in finditer(r"\S+", sentence.normalized_text):
            word = match.group()
            start = match.start()
            wid = word_ids.get(word)
            if wid is None:
                wid = len(unique_words)
                word_ids[word] = wid
                unique_words.append(word)
                word_occ[wid] = array("i")
            word_occ[wid].append(sentence.sentence_id)
            word_occ[wid].append(start)

    print(f"  Unique words: {len(unique_words):,}")

    # -- 2. Intra-word seed index --------------------------------------
    intra: dict[str, array] = {}              # seed -> [wid, offset, ...]

    for wid, word in enumerate(unique_words):
        for offset in range(len(word) - q + 1):
            seed = word[offset : offset + q]
            if seed not in intra:
                intra[seed] = array("i")
            intra[seed].append(wid)
            intra[seed].append(offset)

    print(f"  Intra-word seed keys: {len(intra):,}")

    # -- 3. Boundary seed index (NO SeedOccurrence objects!) -----------
    boundary: dict[str, array] = {}           # seed -> [sid, pos, ...]

    for i, sentence in enumerate(sentences):
        if i > 0 and i % 500_000 == 0:
            print(f"  Boundary seeds: {i:,} / {total:,}")
        text = sentence.normalized_text
        for pos in range(len(text) - q + 1):
            seed = text[pos : pos + q]
            if " " not in seed:
                continue
            if seed not in boundary:
                boundary[seed] = array("i")
            boundary[seed].append(sentence.sentence_id)
            boundary[seed].append(pos)

    elapsed_build = time.time() - t0
    print(f"  Boundary seed keys: {len(boundary):,}")
    print(f"  Index built in {elapsed_build:.1f}s")

    # -- 4. Write binary cache -----------------------------------------
    print("  Writing cache to disk...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        # Header
        f.write(CACHE_MAGIC)
        f.write(struct.pack("<IIII", CACHE_VERSION, q, total,
                            len(unique_words)))

        # Sentences
        for s in sentences:
            f.write(struct.pack("<ii", s.sentence_id, s.offset))
            _write_str(f, s.original_text)
            _write_str(f, s.normalized_text)
            _write_str(f, s.source_path)

        # Unique words
        for w in unique_words:
            _write_str(f, w)

        # Word occurrences
        f.write(struct.pack("<I", len(word_occ)))
        for wid, arr in word_occ.items():
            f.write(struct.pack("<I", wid))
            _write_array(f, arr)

        # Intra-word seeds
        f.write(struct.pack("<I", len(intra)))
        for seed, arr in intra.items():
            _write_str(f, seed)
            _write_array(f, arr)

        # Boundary seeds
        f.write(struct.pack("<I", len(boundary)))
        for seed, arr in boundary.items():
            _write_str(f, seed)
            _write_array(f, arr)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    elapsed_total = time.time() - t0
    print(f"Cache saved: {output_path} ({size_mb:.1f} MB, {elapsed_total:.1f}s)")

    return CachedSeedLookup(
        q=q,
        word_occurrences=word_occ,
        intra_word_seeds=intra,
        boundary_seeds=boundary,
    )


# ------------------------------------------------------------------
# Load  (all subsequent runs — seconds, not minutes)
# ------------------------------------------------------------------

def load_cache(
    cache_path: Path,
) -> tuple[list[PreparedSentence], CachedSeedLookup]:
    """Load sentences and the full Bi-Anchor index from the binary cache.

    Returns (sentences, seed_lookup) ready for immediate search.
    """
    t0 = time.time()
    print("Loading Bi-Anchor cache from disk...")

    with open(cache_path, "rb") as f:
        # Header
        magic = f.read(4)
        if magic != CACHE_MAGIC:
            raise ValueError(f"Invalid cache file (bad magic: {magic!r})")
        version, q, num_sentences, num_words = struct.unpack("<IIII", f.read(16))
        if version != CACHE_VERSION:
            raise ValueError(f"Unsupported cache version: {version}")

        # Sentences
        sentences: list[PreparedSentence] = []
        for _ in range(num_sentences):
            sid, offset = struct.unpack("<ii", f.read(8))
            original = _read_str(f)
            normalized = _read_str(f)
            src_path = _read_str(f)
            sentences.append(PreparedSentence(
                sentence_id=sid,
                original_text=original,
                normalized_text=normalized,
                source_path=src_path,
                offset=offset,
            ))

        # Unique words (stored for completeness, not needed at runtime)
        for _ in range(num_words):
            _read_str(f)

        # Word occurrences
        (n,) = struct.unpack("<I", f.read(4))
        word_occ: dict[int, array] = {}
        for _ in range(n):
            (wid,) = struct.unpack("<I", f.read(4))
            word_occ[wid] = _read_array(f)

        # Intra-word seeds
        (n,) = struct.unpack("<I", f.read(4))
        intra_seeds: dict[str, array] = {}
        for _ in range(n):
            seed = _read_str(f)
            intra_seeds[seed] = _read_array(f)

        # Boundary seeds
        (n,) = struct.unpack("<I", f.read(4))
        boundary_seeds: dict[str, array] = {}
        for _ in range(n):
            seed = _read_str(f)
            boundary_seeds[seed] = _read_array(f)

    lookup = CachedSeedLookup(
        q=q,
        word_occurrences=word_occ,
        intra_word_seeds=intra_seeds,
        boundary_seeds=boundary_seeds,
    )

    elapsed = time.time() - t0
    print(f"Cache loaded: {len(sentences):,} sentences, "
          f"{len(intra_seeds):,} intra seeds, "
          f"{len(boundary_seeds):,} boundary seeds ({elapsed:.1f}s)")

    return sentences, lookup
