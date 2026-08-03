from pathlib import Path

from aegis_ai.assistant import AegisAssistant
from aegis_ai.memory import MemoryStore


def build_assistant(tmp_path: Path) -> AegisAssistant:
    return AegisAssistant(memory=MemoryStore(tmp_path / "memory.txt"))


def test_wake_word_and_calculator(tmp_path: Path) -> None:
    assistant = build_assistant(tmp_path)

    assert assistant.respond("hey aegis calculate (42 * 7) / 3") == "The result is 98.0."


def test_memory_round_trip(tmp_path: Path) -> None:
    assistant = build_assistant(tmp_path)

    assert assistant.respond("jarvis remember arc reactor offline") == "Logged that for you: arc reactor offline"
    assert "arc reactor offline" in assistant.respond("recall notes")


def test_shutdown_detection_strips_wake_word(tmp_path: Path) -> None:
    assistant = build_assistant(tmp_path)

    assert assistant.respond("aegis shutdown") == "Shutting down. Until next time."
    assert assistant.should_exit("aegis shutdown")
