# AutoComplete - Person 1

This project contains only **Person 1: Data Preparation (Offline)**.

## Responsibilities

1. Read folders/files recursively.
2. Validate `.txt` files.
3. Prevent the same file from being loaded twice.
4. Read each line as one sentence.
5. Normalize each sentence.
6. Split normalized text into words and store character positions.
7. Keep sentence metadata.
8. Output `list[PreparedSentence]`.

It does **not** build a Trie, HashMap, Q-gram index, search algorithm, scoring,
ranking, or Top-5 results. Those belong to the next stages.

## Run

Place the assignment archive here:

`data/Archive.zip`

Then:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python src/main.py
```

Tests:

```powershell
pytest
```
