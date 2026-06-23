import csv
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Callable, Any


from constants import INTERFERENCE

DB_PATH = Path("../2025-10-20-trimmed.sqlite")

VOWELS = "aeiou"
CONSONANTS = "jklmnpstw"

SYLLABLE_RE = re.compile(r"(?:[jklmnpstw]?[aeiou]n?)(?:[jklmnpstw][aeiou]n?)*$")
TOKEN_RE = re.compile(r"[jklmnpstw]?[aeiou]n?")


def tokenize_syllables(word: str) -> list[str] | None:
    if not SYLLABLE_RE.fullmatch(word):
        return None
    return TOKEN_RE.findall(word)


def letter_sort_key(letter: str) -> tuple[int, int]:
    if letter in VOWELS:
        return (0, VOWELS.index(letter))
    return (1, CONSONANTS.index(letter))


def syllable_sort_key(syllable: str) -> tuple[int, int, int]:
    coda = syllable.endswith("n")

    base = syllable[:-1] if coda else syllable

    if len(base) == 1:
        onset_rank = -1  # vowel-only first
        vowel = base
    else:
        onset_rank = CONSONANTS.index(base[0])
        vowel = base[1]

    return (
        coda,
        onset_rank,
        VOWELS.index(vowel),
    )


def write_counter_csv(
    path: str,
    column: str,
    counts: dict[str, int],
    sort_key: Callable[[str], Any],
    precision: int = 6,
) -> None:
    total = sum(counts.values())
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([column, "hits", "percent"])
        writer.writerows(
            (
                item,
                counts[item],
                f"{100 * counts[item] / total:.{precision}f}%",
            )
            for item in sorted(counts, key=sort_key)
        )


def main() -> None:
    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute("""
        SELECT t.text, y.hits
        FROM yearly y
        JOIN term t ON y.term_id = t.id
        WHERE t.len = 1
          AND y.attr = 0
          AND y.day = 0
        ORDER BY y.hits ASC
    """)

    letter_counts: Counter[str] = Counter()
    syllable_counts: Counter[str] = Counter()

    total = 0
    accepted = 0

    for word, hits in rows:
        total += 1
        if word in INTERFERENCE:
            continue
        syllables = tokenize_syllables(word)
        if syllables is None:
            continue

        accepted += 1

        for letter in word:
            letter_counts[letter] += hits
        for syllable in syllables:
            syllable_counts[syllable] += hits

    conn.close()

    print(f"Accepted {accepted:,} / {total:,} words")

    write_counter_csv(
        "letters.csv",
        "letter",
        letter_counts,
        letter_sort_key,
    )
    write_counter_csv(
        "syllables.csv",
        "syllable",
        syllable_counts,
        syllable_sort_key,
    )


if __name__ == "__main__":
    main()
