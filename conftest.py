"""Root pytest configuration.

Ensures generated config files exist so the test suites can run on a clean
checkout (e.g. CI) where `config/app/confignew.json` has not been created by
atsetup/docker-init yet. Only writes the file when it is missing — an existing
user config is never overwritten.
"""

from pathlib import Path


def _ensure_default_confignew() -> None:
    config_path = Path(__file__).parent / "config" / "app" / "confignew.json"
    if config_path.exists():
        return
    from config.app.config import AlltalkConfigModel

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(AlltalkConfigModel().model_dump_json(indent=4, by_alias=True))


def pytest_configure():
    _ensure_default_confignew()
