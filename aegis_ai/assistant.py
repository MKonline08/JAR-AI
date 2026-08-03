"""Core assistant orchestration."""

from __future__ import annotations

import re

from .commands import CommandRegistry, build_default_registry
from .memory import MemoryStore


class AegisAssistant:
    """A compact, extensible voice-assistant style brain for text input."""

    wake_patterns = (
        re.compile(r"^hey\s+aegis[,\s]*", re.I),
        re.compile(r"^aegis[,\s]*", re.I),
        re.compile(r"^jarvis[,\s]*", re.I),
    )

    def __init__(self, registry: CommandRegistry | None = None, memory: MemoryStore | None = None) -> None:
        self.registry = registry or build_default_registry()
        self.memory = memory or MemoryStore()

    def respond(self, text: str) -> str:
        cleaned = self._strip_wake_word(text)
        if not cleaned:
            return "Listening."
        if cleaned.lower() in {"exit", "quit", "shutdown", "power down"}:
            return "Shutting down. Until next time."
        return self.registry.dispatch(cleaned, self.memory)

    def should_exit(self, text: str) -> bool:
        cleaned = self._strip_wake_word(text).lower()
        return cleaned in {"exit", "quit", "shutdown", "power down"}

    def _strip_wake_word(self, text: str) -> str:
        cleaned = text.strip()
        for pattern in self.wake_patterns:
            cleaned = pattern.sub("", cleaned, count=1).strip()
        return cleaned
