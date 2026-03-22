from __future__ import annotations

import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


class SettingsManager:
    """Manage application settings with default/actual sync and safe updates.

    Usage:
        mgr = SettingsManager(settings_path, default_settings_path)
        settings = mgr.get_settings()
        mgr.set_settings({"some_key": "new_value"})
    """

    def __init__(self, settings_path: str | Path, default_settings_path: str | Path) -> None:
        self.settings_path = Path(settings_path)
        self.default_settings_path = Path(default_settings_path)

        if not self.default_settings_path.exists():
            raise FileNotFoundError(f"Default settings file not found: {self.default_settings_path}")

        if not self.settings_path.exists():
            # Create parent dir if needed
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.default_settings_path, self.settings_path)

        # Load both and perform version handling (add/remove keys)
        self._settings: Dict[str, Any] = self._load_json(self.settings_path)
        default = self._load_json(self.default_settings_path)

        changed = self._sync_with_default(self._settings, default)
        if changed:
            self._save_json(self.settings_path, self._settings)

    def get_settings(self) -> Dict[str, Any]:
        """Return a deep copy of current settings."""
        return deepcopy(self._settings)

    def set_settings(self, updates: Dict[str, Any]) -> None:
        """Update only existing keys in the settings with values from `updates`.

        Nested dictionaries are handled recursively. Any keys in `updates` that
        do not exist in current settings are ignored.
        """
        if not isinstance(updates, dict):
            raise TypeError("updates must be a dict")

        changed = self._update_existing(self._settings, updates)
        if changed:
            self._save_json(self.settings_path, self._settings)

    # --- Internal helpers ---
    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError(f"Settings file must contain a JSON object: {path}")
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in settings file {path}: {e}")

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        # atomic-ish write: write to temp file then replace
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(path)

    def _sync_with_default(self, actual: Dict[str, Any], default: Dict[str, Any]) -> bool:
        """Add missing keys from default and remove keys not present in default.

        Returns True if any changes were made to `actual`.
        """
        changed = False

        # Add missing keys and recurse for nested dicts
        for k, dv in default.items():
            if k not in actual:
                actual[k] = deepcopy(dv)
                changed = True
            else:
                av = actual[k]
                if isinstance(dv, dict) and isinstance(av, dict):
                    if self._sync_with_default(av, dv):
                        changed = True

        # Remove keys not in default
        for k in list(actual.keys()):
            if k not in default:
                del actual[k]
                changed = True

        return changed

    def _update_existing(self, settings: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Recursively update only keys that already exist in `settings`.

        Returns True if any change was made.
        """
        changed = False
        for k, v in updates.items():
            if k not in settings:
                continue
            if isinstance(settings[k], dict) and isinstance(v, dict):
                if self._update_existing(settings[k], v):
                    changed = True
            else:
                if settings[k] != v:
                    settings[k] = v
                    changed = True

        return changed


__all__ = ["SettingsManager"]
