"""User-controlled capability permissions for desktop integrations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class PermissionSettings:
    """Persisted opt-in permissions for higher-impact assistant features."""

    microphone: bool = False
    webcam: bool = False
    filesystem: bool = False
    shell: bool = False
    allowed_directories: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "PermissionSettings":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{key: data.get(key, value) for key, value in asdict(cls()).items()})

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def can_access_path(self, candidate: Path) -> bool:
        if not self.filesystem:
            return False
        if not self.allowed_directories:
            return True
        resolved = candidate.expanduser().resolve()
        for directory in self.allowed_directories:
            root = Path(directory).expanduser().resolve()
            if resolved == root or root in resolved.parents:
                return True
        return False
