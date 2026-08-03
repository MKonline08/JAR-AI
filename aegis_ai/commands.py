"""Command routing and built-in assistant capabilities."""

from __future__ import annotations

import ast
import datetime as dt
import math
import operator
import os
import platform
import random
import re
from dataclasses import dataclass
from typing import Callable

from .memory import MemoryStore

Handler = Callable[[str, MemoryStore], str]


@dataclass(frozen=True)
class Command:
    """A single assistant command."""

    name: str
    description: str
    patterns: tuple[re.Pattern[str], ...]
    handler: Handler

    def matches(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.patterns)


class CommandRegistry:
    """Routes user text to the first matching command."""

    def __init__(self, commands: list[Command]) -> None:
        self.commands = commands

    def dispatch(self, text: str, memory: MemoryStore) -> str:
        normalized = text.strip().lower()
        for command in self.commands:
            if command.matches(normalized):
                return command.handler(text.strip(), memory)
        return fallback_response(text)

    def help_text(self) -> str:
        lines = ["Available systems:"]
        lines.extend(f"- {command.name}: {command.description}" for command in self.commands)
        return "\n".join(lines)


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(expression: str) -> float | int:
    node = ast.parse(expression, mode="eval")
    return _eval_node(node.body)


def _eval_node(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


def greet(_: str, __: MemoryStore) -> str:
    return random.choice([
        "Good to see you. All systems are ready.",
        "At your service. What shall we build today?",
        "Online and attentive. How may I assist?",
    ])


def report_time(_: str, __: MemoryStore) -> str:
    now = dt.datetime.now().astimezone()
    return f"It is {now:%I:%M %p} on {now:%A, %B %d, %Y}."


def calculate(text: str, _: MemoryStore) -> str:
    expression = re.sub(r"^(calculate|compute|what is|what's)\s+", "", text, flags=re.I).strip()
    try:
        result = _safe_eval(expression)
    except Exception:
        return "I can calculate arithmetic with numbers, parentheses, and + - * / ** operators."
    return f"The result is {result}."


def remember(text: str, memory: MemoryStore) -> str:
    note = re.sub(r"^(remember|note|log)\s+", "", text, flags=re.I).strip()
    if not note:
        return "Tell me what to remember, and I will store it."
    memory.add(note)
    return f"Logged that for you: {note}"


def recall(_: str, memory: MemoryStore) -> str:
    notes = memory.list()
    if not notes:
        return "Memory is currently clear."
    return "Here is what I have stored:\n" + "\n".join(f"- {note}" for note in notes)


def status(_: str, __: MemoryStore) -> str:
    load = os.getloadavg()[0] if hasattr(os, "getloadavg") else math.nan
    load_text = "unavailable" if math.isnan(load) else f"{load:.2f}"
    return f"Systems nominal. Host: {platform.node() or 'unknown'}, OS: {platform.system()} {platform.release()}, CPU load average: {load_text}."


def reminder(text: str, _: MemoryStore) -> str:
    reminder_text = re.sub(r"^(remind me to|reminder|remind)\s+", "", text, flags=re.I).strip()
    if not reminder_text:
        return "Tell me the reminder details and I will stage them."
    return f"Reminder staged: {reminder_text}. Connect a calendar provider to schedule notifications."


def fallback_response(text: str) -> str:
    return (
        "I do not have that subsystem yet, but I can help with time, calculations, "
        "notes, reminders, status, and help. You said: " + text
    )


def build_default_registry() -> CommandRegistry:
    registry: CommandRegistry | None = None

    def help_handler(_: str, __: MemoryStore) -> str:
        assert registry is not None
        return registry.help_text()

    commands = [
        Command("greet", "Respond to greetings.", (re.compile(r"\b(hello|hi|good morning|good evening)\b"),), greet),
        Command("time", "Report the local date and time.", (re.compile(r"\b(time|date)\b"),), report_time),
        Command("calculate", "Safely evaluate arithmetic.", (re.compile(r"^(calculate|compute|what is|what's)\b"),), calculate),
        Command("remember", "Store a persistent note.", (re.compile(r"^(remember|note|log)\b"),), remember),
        Command("recall", "List stored notes.", (re.compile(r"\b(recall|memory|notes)\b"),), recall),
        Command("reminder", "Stage a reminder message.", (re.compile(r"^(remind me to|reminder|remind)\b"),), reminder),
        Command("status", "Summarize basic system status.", (re.compile(r"\b(status|systems|diagnostics)\b"),), status),
        Command("help", "Show available commands.", (re.compile(r"\b(help|commands|capabilities)\b"),), help_handler),
    ]
    registry = CommandRegistry(commands)
    return registry
