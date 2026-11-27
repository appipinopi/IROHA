#!/usr/bin/env python3
"""Create a new dictionary package by merging reviewed four-column additions."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from build_dictionary import build_sqlite_from_tsv, sha256_file, write_checksums

SHARD_ROWS = 250_000


def read_tsv(path: Path, *, validate_hiragana: bool) -> list[tuple[str, str, str, int]]:
    rows: list[tuple[str, str, str, int]] = []
    with path.open("r", encoding="utf-8", newline="") as stream:
        for line_no, raw in enumerate(stream, 1):
            line = raw.rstrip("\r\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) != 4:
                raise ValueError(f"Expected 4 tab-separated fields at {path}:{line_no}")
            surface, reading, pos, cost_text = fields
            if not surface or not reading or not pos:
                raise ValueError(f"Empty field at {path}:{line_no}")
            if any(ch.isspace() for part in (surface, reading, pos) for ch in part):
                raise ValueError(f"Whitespace is not allowed inside fields at {path}:{line_no}")
            try:
                cost = int(cost_text)
            except ValueError as exc:
                raise ValueError(f"Cost must be an integer at {path}:{line_no}") from exc
            if validate_hiragana:
                if not any("\u3041" <= ch <= "\u3096" for ch in reading):
                    raise ValueError(f"Reading must contain hiragana at {path}:{line_no}")
                if any("\u30a1" <= ch <= "\u30f6" for ch in reading):
                    raise ValueError(f"Use hiragana, not katakana, in the reading at {path}:{line_no}")
            rows.append((surface, reading, pos, cost))
    return rows


def write_shards(rows: list[tuple[str, str, str, int]], tsv_dir: Path) -> list[Path]:
    tsv_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for start in range(0, len(rows), SHARD_ROWS):
        number = start // SHARD_ROWS + 1
        path = tsv_dir / f"dictionary-{number:03d}.tsv"
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for surface, reading, pos, cost in rows[start : start + SHARD_ROWS]:
                stream.write(f"{surface}\t{reading}\t{pos}\t{cost}\n")
        paths.append(path)
    return paths


def make_readme(version: str, base_count: int, count: int) -> str:
    return f"""# UniDic 日本語IME辞書（{version}・追加データ統合版）

UniDic {version}を元にした{base_count:,}件の基礎辞書に、追加候補を統合した配布物です。合計 {count:,} 件を収録しています。Mozcには依存しません。

## 内容

- `tsv/`: UTF-8・ヘッダーなし・タブ区切りの4列（表記、ひらがな読み、品詞、コスト）
- `dictionary.sqlite3`: `entries(surface, reading, pos, cost)` テーブルを持つSQLiteデータベース
- `manifest.json` と `SHA256SUMS.txt`: 件数・生成情報・ファイルハッシュ
- `LICENSE-BSD.txt` と `NOTICE.txt`: UniDic由来データの表示
- `supplemental/additions.tsv` と `SUPPLEMENTAL-NOTICE.txt`: 追加語と、その出典・権利情報

出典表示は各レコードやSQLiteの列に入れていません。再配布時はUniDicのNOTICE/LICENSEに加え、追加データに関する表示も保持してください。UniDicおよび国立国語研究所による推奨・承認を示すものではありません。

`cost` は特定IMEの候補順位に合わせて調整していません。実装先IMEで評価してください。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, required=True, help="directory containing manifest.json and tsv/")
    parser.add_argument("--additions-tsv", type=Path, required=True, help="four-column, headerless TSV of additions")
    parser.add_argument("--source-notice", type=Path, required=True, help="completed provenance/rights notice for additions")
    parser.add_argument("--license-file", type=Path, default=Path("LICENSE-BSD.txt"), help="UniDic license text")
    parser.add_argument("--notice-file", type=Path, default=Path("NOTICE.txt"), help="UniDic attribution notice")
    parser.add_argument("--output-dir", type=Path, required=True, help="new output directory; existing contents are never overwritten")
    args = parser.parse_args()

    base_dir = args.base_dir.resolve()
    additions_path = args.additions_tsv.resolve()
    source_notice = args.source_notice.resolve()
    license_file = args.license_file.resolve()
    notice_file = args.notice_file.resolve()
    output_dir = args.output_dir.resolve()
    manifest_path = base_dir / "manifest.json"
    tsv_files = sorted((base_dir / "tsv").glob("dictionary-*.tsv"))
    for required in (manifest_path, additions_path, source_notice, license_file, notice_file):
        if not required.is_file():
            parser.error(f"required file not found: {required}")
    if not tsv_files:
        parser.error(f"no tsv/dictionary-*.tsv files found in {base_dir}")
    if output_dir.exists() and any(output_dir.iterdir()):
        parser.error(f"output directory is not empty: {output_dir}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        base_rows: list[tuple[str, str, str, int]] = []
        seen: set[tuple[str, str, str]] = set()
        for path in tsv_files:
            for row in read_tsv(path, validate_hiragana=False):
                key = row[:3]
                if key in seen:
                    raise ValueError(f"Duplicate key in base TSVs: {key!r}")
                seen.add(key)
                base_rows.append(row)
        additions = read_tsv(additions_path, validate_hiragana=True)
        if not additions:
            raise ValueError("The additions TSV has no data rows")
        if not source_notice.read_text(encoding="utf-8").strip():
            raise ValueError("The supplemental source notice is empty")
        for row in additions:
            key = row[:3]
            if key in seen:
                raise ValueError(f"Addition duplicates an existing dictionary key: {key!r}")
            seen.add(key)
        rows = sorted(base_rows + additions, key=lambda row: (row[1], row[0], row[2], row[3]))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    output_dir.mkdir(parents=True, exist_ok=True)
    tsv_paths = write_shards(rows, output_dir / "tsv")
    count = build_sqlite_from_tsv(tsv_paths, output_dir / "dictionary.sqlite3")
    if count != len(rows):
        raise RuntimeError(f"SQLite row count mismatch: {count} != {len(rows)}")

    shutil.copy2(license_file, output_dir / "LICENSE-BSD.txt")
    shutil.copy2(notice_file, output_dir / "NOTICE.txt")
    with (output_dir / "NOTICE.txt").open("a", encoding="utf-8") as stream:
        stream.write("\n\n追加データの出典・権利表示は SUPPLEMENTAL-NOTICE.txt に記載しています。\n")
    (output_dir / "SUPPLEMENTAL-NOTICE.txt").write_text(source_notice.read_text(encoding="utf-8"), encoding="utf-8")
    supplemental_dir = output_dir / "supplemental"
    supplemental_dir.mkdir()
    shutil.copy2(additions_path, supplemental_dir / "additions.tsv")

    version = str(manifest.get("source_version", "unknown"))
    base_count = len(base_rows)
    manifest["record_count"] = count
    manifest["sqlite"] = {
        "file": "dictionary.sqlite3",
        "table": "entries",
        "columns": ["surface TEXT", "reading TEXT", "pos TEXT", "cost INTEGER"],
        "indexes": ["PRIMARY KEY(reading, surface, pos)", "idx_reading_cost_surface", "idx_surface"],
        "row_count": count,
    }
    manifest["tsv_shards"] = [path.relative_to(output_dir).as_posix() for path in tsv_paths]
    manifest["supplemental"] = {
        "file": "supplemental/additions.tsv",
        "source_notice": "SUPPLEMENTAL-NOTICE.txt",
        "record_count": len(additions),
        "sha256": sha256_file(supplemental_dir / "additions.tsv"),
        "source_notice_sha256": sha256_file(output_dir / "SUPPLEMENTAL-NOTICE.txt"),
    }
    manifest["generated_utc"] = datetime.now(timezone.utc).isoformat()
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "README.md").write_text(make_readme(version, base_count, count), encoding="utf-8")

    script_dir = Path(__file__).resolve().parent
    for name in ("build_dictionary.py", "fetch_unidic_source.py", "merge_additions.py"):
        shutil.copy2(script_dir / name, output_dir / name)
    write_checksums(output_dir)
    print(json.dumps({"output_dir": str(output_dir), "records": count, "added_records": len(additions), "tsv_shards": len(tsv_paths)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
