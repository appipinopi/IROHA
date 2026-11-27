#!/usr/bin/env python3
"""Range-extract the required files from the official UniDic 2025-12 ZIP.

This downloads only the ZIP central directory tail and selected members, rather
than the 2.8 GB full archive. Python standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import urllib.request
import zipfile
import zlib
from pathlib import Path

URL = "https://clrd.ninjal.ac.jp/unidic_archive/2512/unidic-cwj-202512_full.zip"
MEMBERS = ("lex.csv", "feature.def", "license/BSD", "README.md")
TAIL_BYTES = 16 * 1024 * 1024
USER_AGENT = "Mozilla/5.0 (compatible; UniDicDictionaryBuilder/1.0)"


def request_range(url: str, start: int, end: int, timeout: int = 120):
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}", "User-Agent": USER_AGENT})
    response = urllib.request.urlopen(req, timeout=timeout)
    content_range = response.headers.get("Content-Range", "")
    if not content_range.startswith(f"bytes {start}-"):
        response.close()
        raise RuntimeError(f"Server did not honor byte range {start}-{end}: {content_range!r}")
    return response


def extract_member(url: str, info: zipfile.ZipInfo, output: Path) -> str:
    if info.flag_bits & 0x1:
        raise RuntimeError(f"Encrypted ZIP member is not supported: {info.filename}")
    header_end = info.header_offset + 4095
    with request_range(url, info.header_offset, header_end) as response:
        local = response.read()
    if local[:4] != b"PK\x03\x04":
        raise RuntimeError(f"Missing ZIP local header for {info.filename}")
    name_len, extra_len = struct.unpack_from("<HH", local, 26)
    data_start = info.header_offset + 30 + name_len + extra_len
    data_end = data_start + info.compress_size - 1
    output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    crc = 0
    sha = hashlib.sha256()

    with request_range(url, data_start, data_end) as response, output.open("wb") as out:
        if info.compress_type == zipfile.ZIP_DEFLATED:
            decoder = zlib.decompressobj(-15)
        elif info.compress_type == zipfile.ZIP_STORED:
            decoder = None
        else:
            raise RuntimeError(f"Unsupported ZIP compression method {info.compress_type}: {info.filename}")
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            decoded = decoder.decompress(block) if decoder else block
            if decoded:
                out.write(decoded)
                written += len(decoded)
                crc = zlib.crc32(decoded, crc)
                sha.update(decoded)
        if decoder:
            decoded = decoder.flush()
            if decoded:
                out.write(decoded)
                written += len(decoded)
                crc = zlib.crc32(decoded, crc)
                sha.update(decoded)

    if written != info.file_size:
        raise RuntimeError(f"Size mismatch for {info.filename}: {written} != {info.file_size}")
    if (crc & 0xFFFFFFFF) != info.CRC:
        raise RuntimeError(f"CRC mismatch for {info.filename}")
    return sha.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path, help="directory for extracted source files")
    parser.add_argument("--url", default=URL, help="official ZIP URL (defaults to the 2025-12 release)")
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    head_req = urllib.request.Request(args.url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(head_req, timeout=30) as response:
        total = int(response.headers["Content-Length"])
    tail_size = min(TAIL_BYTES, total)
    tail_start = total - tail_size
    with request_range(args.url, tail_start, total - 1) as response:
        tail = response.read()
    if len(tail) != tail_size:
        raise RuntimeError(f"ZIP directory tail was truncated: {len(tail)} != {tail_size}")

    sparse_path = output_dir / ".unidic-index-sparse.tmp"
    try:
        with sparse_path.open("wb") as f:
            f.truncate(total)
            f.seek(tail_start)
            f.write(tail)
        with zipfile.ZipFile(sparse_path) as archive:
            infos = {name: archive.getinfo(name) for name in MEMBERS}
        hashes = {}
        output_names = {
            "lex.csv": "lex.csv",
            "feature.def": "feature.def",
            "license/BSD": "license_BSD",
            "README.md": "README.md",
        }
        for name, info in infos.items():
            dest = output_dir / output_names[name]
            hashes[name] = extract_member(args.url, info, dest)
            print(f"Extracted {name}: {info.file_size:,} bytes; SHA-256 {hashes[name]}", flush=True)
    finally:
        sparse_path.unlink(missing_ok=True)
    print(f"Source files saved in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
