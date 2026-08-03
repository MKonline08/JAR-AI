"""Persistent memory for user notes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MemoryStore:
    """A tiny newline-delimited note store."""

    path: Path = field(default_factory=lambda: Path.home() / ".aegis_ai" / "memory.txt")

    def add(self, note: str) -> None:
        cleaned = note.strip()
        if not cleaned:
            raise ValueError("note cannot be empty")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(cleaned + "\n")

    def list(self) -> list[str]:
        if not self.path.exists():
            return []
        return [line.strip() for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
