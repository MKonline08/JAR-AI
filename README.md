# Aegis AI

Aegis AI is a local, Jarvis-inspired desktop and command-line assistant prototype. It is not affiliated with Marvel, Iron Man, or J.A.R.V.I.S.; it demonstrates a personal assistant architecture with a polished conversational style and explicit user-controlled PC permissions.

## Features

- Desktop app for a real PC workflow with chat, permission toggles, microphone capture, webcam capture, and spoken responses.
- Wake-word aware interaction (`aegis`, `jarvis`, or `hey aegis`).
- Built-in intents for greetings, time/date, calculations, notes, reminders, system status, help, and graceful shutdown.
- Small persistent memory file for user notes.
- Optional microphone, webcam, filesystem, and shell integrations that stay disabled until the user enables them.
- Extensible command registry so new capabilities can be added without changing the chat loop.

## Desktop quick start

The desktop UI uses Python's built-in Tkinter. Microphone, webcam, and text-to-speech providers are optional extras because they depend on your OS drivers.

```bash
python -m pip install -e ".[desktop]"
aegis-desktop
```

In the app, explicitly enable the permissions you want:

- **Allow microphone** enables the Listen button.
- **Allow webcam** enables webcam snapshots saved to `~/.aegis_ai/webcam_capture.jpg`.
- **Allow files** and **Add allowed folder** let you scope file access to chosen directories.
- **Allow shell** enables shell-command integration for trusted local automation code.

## CLI quick start

```bash
python -m aegis_ai
```

Or install in editable mode and use the console script:

```bash
python -m pip install -e .
aegis
```

## Example session

```text
You: hey aegis status
Aegis: Systems nominal. CPU load average ...

You: jarvis remember suit calibration is due Friday
Aegis: Logged that for you: suit calibration is due Friday

You: calculate (42 * 7) / 3
Aegis: The result is 98.
```

## Extending Aegis

Add a new handler in `aegis_ai/commands.py` and register it in `build_default_registry()`. Desktop integrations live behind `DesktopIntegrations` so higher-impact access remains isolated and permission-gated.
