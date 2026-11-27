#!/usr/bin/env python3
"""Fetch the source snapshots used by the IROHA dictionary builder."""
from __future__ import annotations
import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path

SOURCES = {
    "JMdict.gz": "https://www.edrdg.org/pub/Nihongo/JMdict.gz",
    "JMnedict.xml.gz": "https://www.edrdg.org/pub/Nihongo/JMnedict.xml.gz",
}
DEST = Path(__file__).resolve().parent / "source"
USER_AGENT = "IROHA-dictionary-source-fetcher/1.0"


def fetch(name: str, url: str) -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    target = DEST / name
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        digest = hashlib.sha256()
        fd, temp_name = tempfile.mkstemp(prefix=f".{name}.", dir=DEST)
        try:
            with os.fdopen(fd, "wb") as out:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    out.write(block)
                    digest.update(block)
            os.replace(temp_name, target)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
    print(f"{name}\t{target.stat().st_size}\t{digest.hexdigest()}\t{url}")


def main() -> None:
    for name, url in SOURCES.items():
        fetch(name, url)


if __name__ == "__main__":
    main()
