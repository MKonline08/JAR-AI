"""Tkinter desktop app for Aegis AI."""

from __future__ import annotations

import threading
from pathlib import Path
from tkinter import BooleanVar, END, LEFT, RIGHT, BOTH, X, Button, Checkbutton, Entry, Frame, Label, Text, Tk, filedialog, messagebox

from .assistant import AegisAssistant
from .integrations import DesktopIntegrations, IntegrationUnavailable
from .permissions import PermissionSettings

CONFIG_PATH = Path.home() / ".aegis_ai" / "permissions.json"
CAPTURE_PATH = Path.home() / ".aegis_ai" / "webcam_capture.jpg"


class AegisDesktopApp:
    """Desktop control center with opt-in PC capabilities."""

    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Aegis AI Desktop")
        self.root.geometry("820x620")
        self.permissions = PermissionSettings.load(CONFIG_PATH)
        self.integrations = DesktopIntegrations(self.permissions)
        self.assistant = AegisAssistant()

        self.microphone_var = BooleanVar(value=self.permissions.microphone)
        self.webcam_var = BooleanVar(value=self.permissions.webcam)
        self.filesystem_var = BooleanVar(value=self.permissions.filesystem)
        self.shell_var = BooleanVar(value=self.permissions.shell)

        self._build_ui()
        self._append("Aegis", "Desktop systems online. Enable permissions explicitly before using PC integrations.")

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        Label(self.root, text="Aegis AI", font=("Arial", 22, "bold")).pack(pady=8)
        Label(self.root, text="Jarvis-inspired local assistant with opt-in microphone, webcam, file, and shell controls.").pack()

        permission_frame = Frame(self.root)
        permission_frame.pack(fill=X, padx=12, pady=10)
        Checkbutton(permission_frame, text="Allow microphone", variable=self.microphone_var, command=self._save_permissions).pack(side=LEFT)
        Checkbutton(permission_frame, text="Allow webcam", variable=self.webcam_var, command=self._save_permissions).pack(side=LEFT)
        Checkbutton(permission_frame, text="Allow files", variable=self.filesystem_var, command=self._save_permissions).pack(side=LEFT)
        Checkbutton(permission_frame, text="Allow shell", variable=self.shell_var, command=self._save_permissions).pack(side=LEFT)
        Button(permission_frame, text="Add allowed folder", command=self._add_folder).pack(side=RIGHT)

        self.transcript = Text(self.root, wrap="word", height=24)
        self.transcript.pack(fill=BOTH, expand=True, padx=12, pady=8)

        input_frame = Frame(self.root)
        input_frame.pack(fill=X, padx=12, pady=8)
        self.input = Entry(input_frame)
        self.input.pack(side=LEFT, fill=X, expand=True)
        self.input.bind("<Return>", lambda _: self._send_text())
        Button(input_frame, text="Send", command=self._send_text).pack(side=LEFT, padx=4)
        Button(input_frame, text="🎙 Listen", command=self._listen).pack(side=LEFT, padx=4)
        Button(input_frame, text="📷 Capture", command=self._capture).pack(side=LEFT, padx=4)
        Button(input_frame, text="🔊 Speak last", command=self._speak_last).pack(side=LEFT, padx=4)

    def _save_permissions(self) -> None:
        self.permissions.microphone = self.microphone_var.get()
        self.permissions.webcam = self.webcam_var.get()
        self.permissions.filesystem = self.filesystem_var.get()
        self.permissions.shell = self.shell_var.get()
        self.permissions.save(CONFIG_PATH)

    def _add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Allow Aegis to access this folder")
        if folder and folder not in self.permissions.allowed_directories:
            self.permissions.allowed_directories.append(folder)
            self.permissions.filesystem = True
            self.filesystem_var.set(True)
            self.permissions.save(CONFIG_PATH)
            self._append("Aegis", f"Allowed folder added: {folder}")

    def _send_text(self) -> None:
        text = self.input.get().strip()
        if not text:
            return
        self.input.delete(0, END)
        self._append("You", text)
        response = self.assistant.respond(text)
        self._append("Aegis", response)

    def _listen(self) -> None:
        self._run_background(lambda: self.integrations.listen_once(), self._handle_voice_text)

    def _handle_voice_text(self, text: str) -> None:
        self.input.delete(0, END)
        self.input.insert(0, text)
        self._send_text()

    def _capture(self) -> None:
        self._run_background(lambda: self.integrations.capture_webcam(CAPTURE_PATH), lambda path: self._append("Aegis", f"Webcam image saved to {path}"))

    def _speak_last(self) -> None:
        text = self._last_aegis_message()
        if text:
            self._run_background(lambda: self.integrations.speak(text), lambda _: None)

    def _run_background(self, job, on_success) -> None:
        def worker() -> None:
            try:
                result = job()
            except (PermissionError, IntegrationUnavailable, Exception) as exc:
                self.root.after(0, lambda: messagebox.showwarning("Aegis AI", str(exc)))
            else:
                self.root.after(0, lambda: on_success(result))
        threading.Thread(target=worker, daemon=True).start()

    def _append(self, speaker: str, text: str) -> None:
        self.transcript.insert(END, f"{speaker}: {text}\n\n")
        self.transcript.see(END)

    def _last_aegis_message(self) -> str:
        content = self.transcript.get("1.0", END).strip().split("\n\n")
        for block in reversed(content):
            if block.startswith("Aegis: "):
                return block.removeprefix("Aegis: ")
        return ""


def main() -> int:
    AegisDesktopApp().run()
    return 0
