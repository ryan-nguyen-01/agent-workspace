"""Shared generator helper: write generated files with manual-edit (hash) conflict detection.

Adapted from the ADLC sync pattern (per-file SHA256 manifest + conflict detection). Each generator
records the SHA256 of what it last wrote in .runtime/context/.generated.json (gitignored, local).
Before overwriting, if the file on disk differs from BOTH the new content AND the last recorded hash,
it was hand-edited — the generator refuses to clobber it unless --force (R-018-06).

Usage in a generator:
    from _genlib import Generator
    gen = Generator("build-codex-prompts", force=args.force)
    for path, content in artifacts.items():
        gen.write(path, content)
    gen.flush()
    return gen.report()        # prints summary; returns exit code (1 if blocked manual edits)

Check mode (no writes):
    gen = Generator("build-plugin", check=True)
    for path, content in artifacts.items():
        gen.check(path, content)
    return gen.report()
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".runtime" / "context" / ".generated.json"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Generator:
    def __init__(self, name: str, *, force: bool = False, check: bool = False) -> None:
        self.name = name
        self.force = force
        self.check_mode = check
        self.manifest = self._load()
        self.written: list[str] = []
        self.unchanged: list[str] = []
        self.manual_edits: list[str] = []   # hand-edited; refused (write) / drift (check)
        self.drift: list[str] = []          # disk != expected new content (check mode)

    def _load(self) -> dict:
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _rel(self, path: Path) -> str:
        return Path(path).resolve().relative_to(ROOT).as_posix()

    def write(self, path: Path, content: str) -> str:
        path = Path(path)
        rel = self._rel(path)
        new_hash = _sha(content)
        if path.exists():
            disk = path.read_text(encoding="utf-8", errors="ignore")
            disk_hash = _sha(disk)
            if disk_hash == new_hash:
                self.manifest[rel] = {"sha256": new_hash, "by": self.name}
                self.unchanged.append(rel)
                return "unchanged"
            recorded = self.manifest.get(rel, {}).get("sha256")
            if recorded and disk_hash != recorded and not self.force:
                self.manual_edits.append(rel)
                return "manual-edit"   # do not clobber a hand-edited file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.manifest[rel] = {"sha256": new_hash, "by": self.name}
        self.written.append(rel)
        return "written"

    def check(self, path: Path, content: str) -> str:
        path = Path(path)
        rel = self._rel(path)
        if not path.exists():
            self.drift.append(rel + " (missing)")
            return "missing"
        disk = path.read_text(encoding="utf-8", errors="ignore")
        if _sha(disk) != _sha(content):
            recorded = self.manifest.get(rel, {}).get("sha256")
            if recorded and _sha(disk) == recorded:
                self.drift.append(rel + " (source changed)")
            else:
                self.manual_edits.append(rel + " (hand-edited)")
            return "drift"
        return "ok"

    def flush(self) -> None:
        if self.check_mode:
            return
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(self.manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def report(self) -> int:
        if self.manual_edits:
            verb = "drift (hand-edited)" if self.check_mode else "refused (hand-edited, use --force)"
            print(f"[{self.name}] manual-edit {verb}: {self.manual_edits}")
        if self.drift:
            print(f"[{self.name}] drift: {self.drift}")
        if not self.check_mode and (self.written or self.unchanged):
            print(f"[{self.name}] wrote {len(self.written)}, unchanged {len(self.unchanged)}")
        return 1 if (self.manual_edits or self.drift) else 0
