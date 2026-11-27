#!/usr/bin/env python3
"""Build a quality-filtered Japanese IME dictionary from UniDic 2025-12 lex.csv.

Output records have exactly four TSV fields: surface, hiragana reading, POS, cost.
The SQLite database is built by reading those TSV shards and contains no source
or attribution fields. All source/licensing information remains in sidecars.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

UNIDIC_VERSION = "2025-12"
UNIDIC_SOURCE_URL = "https://clrd.ninjal.ac.jp/unidic_archive/2512/unidic-cwj-202512_full.zip"
UNIDIC_INFO_URL = "https://clrd.ninjal.ac.jp/unidic/back_number.html"
LICENSE_URL = "https://clrd.ninjal.ac.jp/unidic/copying/BSD"
# UniDic CSV: orthBase (14) is the canonical spelling; lForm (10) is its
# conventional kana form, while pron (13) supplies source-backed variants.
SURFACE_COL = 14
ORTH_COL = 12
COST_COL = 3
POS_COLS = (4, 5, 6, 7)
READING_COLS = (10, 13)
ALLOWED_SURFACE_PUNCTUATION = set("・＝-‐‑–—")
ALLOWED_READING_PUNCTUATION = {"・"}
SHARD_ROWS = 250_000
BATCH_ROWS = 10_000


def to_hiragana(value: str) -> str:
    """Normalize katakana pronunciation for Japanese IME input."""
    value = unicodedata.normalize("NFKC", value.strip())
    out: list[str] = []
    for ch in value:
        cp = ord(ch)
        if 0x30A1 <= cp <= 0x30F6:
            out.append(chr(cp - 0x60))
        elif ch == "ヷ":
            out.append("わ\u3099")
        elif ch == "ヸ":
            out.append("ゐ\u3099")
        elif ch == "ヹ":
            out.append("ゑ\u3099")
        elif ch == "ヺ":
            out.append("を\u3099")
        else:
            out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def has_hiragana(value: str) -> bool:
    return any("\u3041" <= ch <= "\u3096" for ch in value)


def has_unsupported_punctuation(value: str, allowed: set[str]) -> bool:
    return any(unicodedata.category(ch)[0] in "PS" and ch not in allowed for ch in value)


def is_kana_only_surface(value: str) -> bool:
    normalized = unicodedata.normalize("NFKC", value)
    allowed_marks = "ーゝゞヽヾ"
    return bool(normalized) and all(
        "\u3040" <= ch <= "\u309f" or "\u30a0" <= ch <= "\u30ff" or ch in allowed_marks
        for ch in normalized
    )


def has_intrusive_mixed_kana(value: str) -> bool:
    """Reject a lone kana from the other script inserted inside a kana run."""
    value = unicodedata.normalize("NFKC", value)
    hira = [i for i, ch in enumerate(value) if "\u3041" <= ch <= "\u3096"]
    kata = [i for i, ch in enumerate(value) if "\u30a1" <= ch <= "\u30f6"]
    if not hira or not kata or len(hira) == len(kata):
        return False
    minority, majority = (kata, hira) if len(kata) < len(hira) else (hira, kata)
    if len(minority) != 1:
        return False
    index = minority[0]
    if index == 0 or index == len(value) - 1:
        return False
    return index - 1 in majority and index + 1 in majority


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_entries(source_csv: Path) -> tuple[list[tuple[str, str, str, int]], dict]:
    # key: (surface, reading, pos); repeated rows keep the lower source cost.
    dedup: dict[tuple[str, str, str], int] = {}
    rejected: Counter[str] = Counter()
    source_records = 0
    canonical_source_records = 0
    accepted_reading_entries = 0

    with source_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for line_no, row in enumerate(reader, start=1):
            source_records += 1
            if len(row) <= max(POS_COLS + READING_COLS + (SURFACE_COL, ORTH_COL, COST_COL)):
                rejected["too_few_columns"] += 1
                continue

            surface = unicodedata.normalize("NFC", row[SURFACE_COL].strip())
            orth = unicodedata.normalize("NFC", row[ORTH_COL].strip())
            pos_levels = [v.strip() for v in (row[i] for i in POS_COLS) if v.strip() and v.strip() != "*"]
            pos = "/".join(pos_levels)
            if not surface or surface == "*":
                rejected["missing_surface"] += 1
                continue
            if not orth or orth != surface:
                rejected["noncanonical_or_inflected_form"] += 1
                continue
            if not pos:
                rejected["missing_pos"] += 1
                continue
            if any(ch in surface or ch in pos for ch in "\t\r\n"):
                rejected["control_character"] += 1
                continue
            if has_unsupported_punctuation(surface, ALLOWED_SURFACE_PUNCTUATION):
                rejected["unsupported_surface_punctuation_or_symbol"] += 1
                continue
            if has_intrusive_mixed_kana(surface):
                rejected["intrusive_mixed_kana"] += 1
                continue
            if any(ch.isspace() for ch in surface):
                rejected["embedded_whitespace"] += 1
                continue
            if len(surface) > 128:
                rejected["unusually_long"] += 1
                continue
            try:
                cost = int(row[COST_COL])
            except (ValueError, IndexError):
                rejected["invalid_cost"] += 1
                continue

            readings: list[str] = []
            if is_kana_only_surface(surface):
                reading = to_hiragana(surface)
                if has_hiragana(reading) and not has_unsupported_punctuation(reading, ALLOWED_READING_PUNCTUATION):
                    readings.append(reading)
            else:
                for col in READING_COLS:
                    raw_reading = row[col].strip()
                    if not raw_reading or raw_reading == "*":
                        continue
                    if has_intrusive_mixed_kana(raw_reading):
                        rejected["intrusive_mixed_kana_reading"] += 1
                        continue
                    reading = to_hiragana(raw_reading)
                    if not reading or not has_hiragana(reading):
                        continue
                    if any(ch in reading for ch in "\t\r\n") or any(ch.isspace() for ch in reading):
                        continue
                    if has_unsupported_punctuation(reading, ALLOWED_READING_PUNCTUATION) or len(reading) > 256:
                        continue
                    if reading not in readings:
                        readings.append(reading)
            if not readings:
                rejected["missing_or_non_kana_reading"] += 1
                continue

            canonical_source_records += 1
            for reading in readings:
                accepted_reading_entries += 1
                key = (surface, reading, pos)
                previous = dedup.get(key)
                if previous is None or cost < previous:
                    dedup[key] = cost

            if line_no % 500_000 == 0:
                print(f"Parsed {line_no:,} source rows; {len(dedup):,} unique entries so far", flush=True)

    entries = [(surface, reading, pos, cost)
               for (surface, reading, pos), cost in dedup.items()]
    entries.sort(key=lambda row: (row[1], row[0], row[2], row[3]))
    stats = {
        "source_records": source_records,
        "canonical_source_records": canonical_source_records,
        "accepted_reading_entries_before_deduplication": accepted_reading_entries,
        "duplicate_records_collapsed": accepted_reading_entries - len(entries),
        "unique_records": len(entries),
        "rejected_by_reason": dict(sorted(rejected.items())),
    }
    return entries, stats


def write_tsv_shards(entries: list[tuple[str, str, str, int]], tsv_dir: Path) -> list[Path]:
    tsv_dir.mkdir(parents=True, exist_ok=True)
    for old in tsv_dir.glob("dictionary-*.tsv"):
        old.unlink()
    shards: list[Path] = []
    for offset in range(0, len(entries), SHARD_ROWS):
        shard_no = offset // SHARD_ROWS + 1
        path = tsv_dir / f"dictionary-{shard_no:03d}.tsv"
        with path.open("w", encoding="utf-8", newline="\n") as f:
            for surface, reading, pos, cost in entries[offset:offset + SHARD_ROWS]:
                f.write(f"{surface}\t{reading}\t{pos}\t{cost}\n")
        shards.append(path)
    return shards


def build_sqlite_from_tsv(shards: Iterable[Path], db_path: Path) -> int:
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("""CREATE TABLE entries (
            surface TEXT NOT NULL,
            reading TEXT NOT NULL,
            pos TEXT NOT NULL,
            cost INTEGER NOT NULL,
            PRIMARY KEY (reading, surface, pos)
        ) WITHOUT ROWID""")
        count = 0
        batch: list[tuple[str, str, str, int]] = []
        sql = "INSERT INTO entries(surface, reading, pos, cost) VALUES (?, ?, ?, ?)"
        for shard in shards:
            with shard.open("r", encoding="utf-8", newline="") as f:
                for line_no, line in enumerate(f, start=1):
                    fields = line.rstrip("\n").split("\t")
                    if len(fields) != 4:
                        raise ValueError(f"Expected 4 TSV fields in {shard}:{line_no}")
                    surface, reading, pos, cost_text = fields
                    batch.append((surface, reading, pos, int(cost_text)))
                    if len(batch) >= BATCH_ROWS:
                        conn.executemany(sql, batch)
                        count += len(batch)
                        batch.clear()
        if batch:
            conn.executemany(sql, batch)
            count += len(batch)
        conn.execute("CREATE INDEX idx_reading_cost_surface ON entries(reading, cost, surface)")
        conn.execute("CREATE INDEX idx_surface ON entries(surface)")
        conn.commit()
        conn.execute("PRAGMA optimize")
        conn.commit()
        check = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if check != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {check}")
        db_count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        if db_count != count:
            raise RuntimeError(f"SQLite row count mismatch: inserted {count}, stored {db_count}")
        return count
    finally:
        conn.close()


def write_readme(out_dir: Path, stats: dict, shard_names: list[str], csv_sha256: str) -> None:
    text = f"""# UniDic 日本語IME辞書

現代書き言葉UniDicの公式データ（{UNIDIC_VERSION}版）から作成した、日本語IME向けの語彙辞書です。Mozcには依存しません。

## 内容

- `tsv/`: UTF-8のTSV {len(shard_names)}ファイル。合計 {stats['unique_records']:,} 件。ヘッダーなしの各行は、表記・ひらがな読み・品詞・変換コストの4列です。
- `dictionary.sqlite3`: 上記TSVを読み込んで作成した単一のSQLiteファイル。`entries(surface, reading, pos, cost)` テーブルと読み・コスト／表記検索用索引を持ちます。各レコードにもDB内にも出典名・出典タグは含めていません。
- `LICENSE-BSD.txt` と `NOTICE.txt`: ソースと再配布条件の表示。
- `manifest.json` と `SHA256SUMS.txt`: 件数、変換情報、ファイルハッシュ。
- `build_dictionary.py` と `fetch_unidic_source.py`: 再生成用スクリプト。

## 出典とライセンス

出典は[UniDic 2025-12 フル配布物]({UNIDIC_SOURCE_URL})です（[公式バージョン一覧]({UNIDIC_INFO_URL})）。語彙データはアーカイブ内の `lex.csv` を使用し、そのSHA-256は `{csv_sha256}` です。元データに適用される修正BSDライセンスを `LICENSE-BSD.txt` に同梱しています。再配布時には著作権表示・条件・免責を保持してください。表示はこの文書にまとめ、辞書の各行には加えていません。UniDicおよび国立国語研究所が本辞書を推奨・承認していることを示すものではありません。

## 変換内容と注意点

表記にはUniDicの基底表記 `orthBase` を使い、活用形など基底形と一致しない行（`orth` != `orthBase`）は見出し語として登録しません。ひらがな・カタカナだけの表記は表記そのものをひらがな化して読みとし、それ以外は標準的なかな形 `lForm` と発音 `pron` をソース由来の読み候補として採用します。「東京」の通常読み「とうきょう」と発音由来の「とーきょー」のような読み変異も保持します。句読記号・絵文字などを含む表記や読み、表記または読みのかな列の途中に単独で入り込んだ別種のかな表記は除外し、表記・読み・品詞が同一の重複は1件にまとめ、最も低い元コストを残します。単語や読みの捏造・自動生成はしていません。

`cost` はUniDic/Mecab由来の語彙コストであり、特定のIMEの候補順位に合わせて調整した値ではありません。実装に組み込む前に、対象エンジンで評価・調整してください。

## 再生成

Python 3.9以降、標準ライブラリのみで動作します。公式フルZIP全体をダウンロードせず必要ファイルだけ取得するには、`python3 fetch_unidic_source.py --output-dir unidic-source` を実行します。その後、`python3 build_dictionary.py --source-csv unidic-source/lex.csv --output-dir OUTPUT_DIR` を実行します。最初にTSVを作成し、そのTSV群を読み込んでSQLiteを構築します。

## 検査結果

- 元CSVの行数: {stats['source_records']:,}
- 基底形として採用したソース行: {stats['canonical_source_records']:,}
- 重複除去前の読み付きレコード数: {stats['accepted_reading_entries_before_deduplication']:,}
- 統合した重複行: {stats['duplicate_records_collapsed']:,}
- 最終ユニーク件数: {stats['unique_records']:,}
- TSV: {', '.join(shard_names)}
"""
    (out_dir / "README.md").write_text(text, encoding="utf-8")


def write_notice(out_dir: Path, source_lex_sha256: str) -> None:
    text = f"""出典・ライセンス表示
====================

本IME辞書は、現代書き言葉UniDic {UNIDIC_VERSION} フル配布物に含まれる lex.csv を選別・変換して作成しました。

出典: {UNIDIC_SOURCE_URL}
公式バージョン一覧: {UNIDIC_INFO_URL}
UniDicライセンス案内: {LICENSE_URL}

元データの著作権表示:
Copyright (c) 2023 National Institute for Japanese Language and Linguistics
国立国語研究所（言語資源開発センター／「語彙資源」プロジェクト／「BCCWJ2」プロジェクト）

元データは、配布物に同梱された修正BSDライセンス（LICENSE-BSD.txt）に基づいて再配布しています。ライセンス本文の著作権表示・条件・免責を保持してください。ライセンス本文の条件に従い、権利者・貢献者の名称を、事前の書面許可なく派生製品の推奨・宣伝に使用しないでください。ライセンスは商用利用および再配布を許可します。

加工内容: UniDicの基底表記 orthBase を使用し、orth と orthBase が一致する基底形のみを採用しました。ひらがな・カタカナのみの表記はひらがな化し、それ以外はソースの lForm と発音 pron を読み候補として使用、カタカナはひらがなへ変換しました。句読記号・絵文字などを含む表記や読み、表記または読みのかな列の途中に単独で入り込んだ別種のかな表記を除外し、表記・読み・品詞が同一の重複は統合して最も低い元コストを採用しました。出典情報は個々の辞書行・SQLiteレコードには付加していません。

本辞書はUniDicの派生物であり、UniDicまたは国立国語研究所による推奨・承認を示すものではありません。

元CSV（lex.csv）のSHA-256:
{source_lex_sha256}
"""
    (out_dir / "NOTICE.txt").write_text(text, encoding="utf-8")


def write_checksums(out_dir: Path) -> None:
    lines: list[str] = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        rel = path.relative_to(out_dir).as_posix()
        lines.append(f"{sha256_file(path)}  {rel}")
    (out_dir / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    global SHARD_ROWS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", required=True, type=Path, help="official UniDic 2025-12 lex.csv")
    parser.add_argument("--output-dir", required=True, type=Path, help="new or existing output directory")
    parser.add_argument("--shard-rows", type=int, default=SHARD_ROWS, help="records per TSV shard (default: 250000)")
    args = parser.parse_args()
    SHARD_ROWS = args.shard_rows
    if SHARD_ROWS < 1:
        parser.error("--shard-rows must be positive")
    source_csv = args.source_csv.resolve()
    out_dir = args.output_dir.resolve()
    if not source_csv.is_file():
        parser.error(f"source CSV not found: {source_csv}")
    source_license = source_csv.parent / "license_BSD"
    if not source_license.is_file():
        parser.error(f"official license file missing next to CSV: {source_license}; run fetch_unidic_source.py")
    out_dir.mkdir(parents=True, exist_ok=True)
    tsv_dir = out_dir / "tsv"
    has_old_shards = tsv_dir.exists() and any(tsv_dir.glob("dictionary-*.tsv"))
    if (out_dir / "dictionary.sqlite3").exists() or has_old_shards:
        parser.error("output directory already contains generated dictionary files; choose a new directory")

    print("Reading and validating UniDic CSV…", flush=True)
    entries, stats = load_entries(source_csv)
    print(f"Writing {len(entries):,} unique TSV records…", flush=True)
    shards = write_tsv_shards(entries, out_dir / "tsv")
    print("Compiling SQLite from TSV shards…", flush=True)
    db_count = build_sqlite_from_tsv(shards, out_dir / "dictionary.sqlite3")
    if db_count != stats["unique_records"]:
        raise RuntimeError("TSV/SQLite row-count mismatch")

    csv_sha256 = sha256_file(source_csv)
    shutil.copy2(source_license, out_dir / "LICENSE-BSD.txt")
    write_notice(out_dir, csv_sha256)
    shard_names = [p.relative_to(out_dir).as_posix() for p in shards]
    manifest = {
        "dictionary": "UniDic Japanese IME Dictionary",
        "source_version": UNIDIC_VERSION,
        "source_archive": UNIDIC_SOURCE_URL,
        "source_file": "lex.csv",
        "source_file_sha256": csv_sha256,
        "source_license": "Modified BSD; see LICENSE-BSD.txt and NOTICE.txt",
        "schema": ["surface", "reading", "pos", "cost"],
        "text_encoding": "UTF-8",
        "text_delimiter": "TAB",
        "record_count": stats["unique_records"],
        "source_stats": stats,
        "sqlite": {
            "file": "dictionary.sqlite3",
            "table": "entries",
            "columns": ["surface TEXT", "reading TEXT", "pos TEXT", "cost INTEGER"],
            "indexes": ["PRIMARY KEY(reading, surface, pos)", "idx_reading_cost_surface", "idx_surface"],
            "row_count": db_count,
        },
        "tsv_shards": shard_names,
        "transforms": [
            "canonical orthBase entries only where orth equals orthBase; inflected/noncanonical forms excluded",
            "kana-only spellings converted directly to hiragana; other readings from lForm and pron converted from katakana",
            "unsupported punctuation and symbols excluded from surface forms and readings",
            "a single intrusive kana character from the other kana script inside a surface or source reading kana run excluded",
            "POS levels 1-4 joined by slash; missing levels omitted",
            "exact (surface, reading, POS) duplicates collapsed; lowest source cost retained",
            "records without usable fields, with whitespace, or over configured length limits omitted",
        ],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(out_dir, stats, shard_names, csv_sha256)

    # Include reproducibility scripts in the deliverable folder.
    script_dir = Path(__file__).resolve().parent
    for name in ("build_dictionary.py", "fetch_unidic_source.py"):
        src = script_dir / name
        if src.exists():
            shutil.copy2(src, out_dir / name)
    write_checksums(out_dir)
    print(json.dumps({"output_dir": str(out_dir), "records": db_count, "tsv_shards": len(shards), "source_sha256": csv_sha256}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
