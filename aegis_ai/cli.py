"""Command-line interface for Aegis AI."""

from __future__ import annotations

from .assistant import AegisAssistant


def main() -> int:
    assistant = AegisAssistant()
    print("Aegis AI online. Say 'help' for capabilities or 'shutdown' to exit.")
    while True:
        try:
            user_text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nAegis: Shutting down. Until next time.")
            return 0
        response = assistant.respond(user_text)
        print(f"Aegis: {response}")
        if assistant.should_exit(user_text):
            return 0
