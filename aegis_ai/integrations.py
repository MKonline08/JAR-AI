"""Optional desktop, microphone, and webcam integrations."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .permissions import PermissionSettings


class IntegrationUnavailable(RuntimeError):
    """Raised when an optional desktop integration is not installed or enabled."""


@dataclass
class DesktopIntegrations:
    """Adapter layer for capabilities that touch local PC resources."""

    permissions: PermissionSettings

    def listen_once(self, timeout: int = 5) -> str:
        if not self.permissions.microphone:
            raise PermissionError("Microphone access is disabled. Enable it in the desktop app first.")
        try:
            import speech_recognition as sr
        except ImportError as exc:
            raise IntegrationUnavailable("Install the 'voice' extra to enable microphone input.") from exc

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=timeout)
        return recognizer.recognize_google(audio)

    def speak(self, text: str) -> None:
        try:
            import pyttsx3
        except ImportError as exc:
            raise IntegrationUnavailable("Install the 'voice' extra to enable spoken responses.") from exc
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def capture_webcam(self, output_path: Path) -> Path:
        if not self.permissions.webcam:
            raise PermissionError("Webcam access is disabled. Enable it in the desktop app first.")
        try:
            import cv2
        except ImportError as exc:
            raise IntegrationUnavailable("Install the 'vision' extra to enable webcam capture.") from exc

        camera = cv2.VideoCapture(0)
        try:
            if not camera.isOpened():
                raise IntegrationUnavailable("No webcam could be opened.")
            ok, frame = camera.read()
            if not ok:
                raise IntegrationUnavailable("Could not read a frame from the webcam.")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), frame)
            return output_path
        finally:
            camera.release()

    def read_text_file(self, path: Path) -> str:
        if not self.permissions.can_access_path(path):
            raise PermissionError("Filesystem access is disabled or the path is outside allowed directories.")
        return path.expanduser().read_text(encoding="utf-8")

    def run_shell(self, command: str) -> str:
        if not self.permissions.shell:
            raise PermissionError("Shell access is disabled. Enable it only for commands you trust.")
        completed = subprocess.run(command, shell=True, check=False, capture_output=True, text=True, timeout=30)
        output = (completed.stdout + completed.stderr).strip()
        return output or f"Command finished with exit code {completed.returncode}."
