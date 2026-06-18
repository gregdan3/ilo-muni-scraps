from typing import Any
import requests
import importlib.resources
from math import log10
from symspellpy import SymSpell

LINKU = "https://api.linku.la/v2/words"
DATA: dict[str, Any] = requests.get(LINKU).json()
WORDS: list[str] = [
    value["word"] for key, value in DATA.items() if int(value["usage"]["2025-09"]) >= 25
]

sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=24)
dictionary_path = (
    importlib.resources.files("symspellpy") / "frequency_dictionary_en_82_765.txt"
)
bigram_path = (
    importlib.resources.files("symspellpy")
    / "frequency_bigramdictionary_en_243_342.txt"
)

sym_spell.load_dictionary(dictionary_path, 0, 1)
sym_spell.load_bigram_dictionary(bigram_path, 0, 2)


def common_prefix_length(a: str, b: str) -> int:
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n


def main():
    for word in WORDS:
        suggestions = sym_spell.lookup(word, verbosity=9999)
        suggestions = [s for s in suggestions if s.distance > 0 and s.count > 1000]
        ranked = sorted(
            suggestions,
            key=lambda s: (
                (log10(s.count + 1) / 3)
                - 2 * s.distance
                + 0.5 * common_prefix_length(word, s.term)
                - 0.5 * abs(len(s.term) - len(word))  # length difference
            ),
            reverse=True,
        )
        for s in ranked[:5]:
            print(word, s.term, s.distance, log10(s.count + 1))
        # for s in suggestions:
        #     print(word, s.term, s.distance, s.count)


if __name__ == "__main__":
    main()
