from pathlib import Path

from aegis_ai.permissions import PermissionSettings


def test_permission_settings_round_trip(tmp_path: Path) -> None:
    config = tmp_path / "permissions.json"
    settings = PermissionSettings(microphone=True, webcam=True, filesystem=True, allowed_directories=[str(tmp_path)])

    settings.save(config)
    loaded = PermissionSettings.load(config)

    assert loaded.microphone
    assert loaded.webcam
    assert loaded.can_access_path(tmp_path / "notes.txt")
    assert not loaded.can_access_path(tmp_path.parent / "private.txt")
