import argparse
import sqlite3
from collections import defaultdict

import requests
from constants import (
    UCSUR_MAP,
    LINKU_URL,
    LINKU_SANDBOX_URL,
    INTERFERENCE,
    DB_PATH,
    DAYS,
)


def fetch_linku_data():
    word_data = requests.get(LINKU_URL).json()
    sandbox_data = requests.get(LINKU_SANDBOX_URL).json()
    return {
        meta["word"]: meta.get("usage_category", "unknown")
        for meta in [*word_data.values(), *sandbox_data.values()]
    }


def get_total_hits(cur, day: int = 0, attr: int = 0, len: int = 1) -> int:
    cur.execute(f"""
        SELECT hits
        FROM total_yearly y
        WHERE y.day = {day}
          AND y.attr = {attr}
          AND y.term_len = {len}
    """)

    row = cur.fetchone()
    return row[0] if row else 0


def get_top_words(
    cur,
    day: int = 0,
    attr: int = 0,
    len: int = 1,
    limit: int = 500,
    no_filter: bool = False,
):
    cur.execute(f"""
        SELECT t.text, y.hits
        FROM yearly y
        JOIN term t ON t.id = y.term_id
        WHERE y.day = {day}
          AND y.attr = {attr}
          AND t.len = {len}
        ORDER BY y.hits DESC
    """)
    rows = cur.fetchall()

    combined = defaultdict(int)
    removed_hits = 0

    for text, hits in rows:
        if (not no_filter) and text in INTERFERENCE:
            removed_hits += hits
            continue
        # Convert UCSUR glyphs to their parent word
        parent = UCSUR_MAP.get(text, text)

        combined[parent] += hits

    reranked = sorted(
        combined.items(),
        key=lambda x: -x[1],
    )

    return reranked[:limit], removed_hits


def cleaned_ranks(cur, day: int = 0, no_filter: bool = False):
    linku = fetch_linku_data()

    rows, to_remove = get_top_words(cur, day)
    total_hits = get_total_hits(cur, day)
    total_hits -= to_remove

    cumulative_pct = 0
    cumulative_hits = 0

    header = "rank,word,category,hits,cumulative_hits,percent,cumulative_percent"
    print(header)
    special = f"0,ALL,,{total_hits},{total_hits},100%,100%"
    print(special)

    for i, (text, hits) in enumerate(rows, start=1):
        category = linku.get(text, "unknown")

        pct = (hits / total_hits * 100) if total_hits else 0

        cumulative_pct += pct
        cumulative_hits += hits

        row = ",".join(
            [
                str(i),
                str(text),
                str(category),
                str(hits),
                str(cumulative_hits),
                f"{pct:.4f}%",
                f"{cumulative_pct:.4f}%",
            ]
        )
        print(row)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--day",
        choices=[
            "ALL",
            "2025",
            "2024",
            "2023",
            "2022",
        ],
        default="ALL",
        help="What year to fetch words from, or all time (default)",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=500,
        help="How many words to fetch, from most to least used.",
    )

    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Disable filtering out known false positives from word list",
    )
    args = parser.parse_args()

    day: int = DAYS[args.day]
    no_filter: bool = args.no_filter

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cleaned_ranks(cur, day, no_filter)


if __name__ == "__main__":
    main()
