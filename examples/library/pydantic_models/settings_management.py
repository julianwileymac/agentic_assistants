# requires: pydantic>=2 pydantic-settings pyyaml

"""Layered configuration with ``BaseSettings``: env, ``.env``, secrets, and YAML."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    """Nested block; override with ``APP_DB__HOST``-style environment variables."""

    host: str = "localhost"
    port: int = 5432
    name: str = "app"


class AppSettings(BaseSettings):
    """
    Resolution order (see pydantic-settings docs for your version):

    1. Environment variables (e.g. ``APP_ENVIRONMENT``)
    2. ``.env`` file (when ``env_file`` is set)
    3. Field defaults

    Use ``secrets_dir`` for Docker/Kubernetes mounted secret files (one file per key).
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    environment: str = "dev"
    api_key: SecretStr = Field(default=SecretStr("default-insecure-key"))
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load optional YAML bootstrap values (application-specific layer)."""
    if not path.is_file():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise TypeError("YAML root must be a mapping")
    return raw


def settings_with_yaml_bootstrap(
    *,
    yaml_path: Path,
    env_file: Path | None,
    secrets_dir: Path | None,
    **env: str,
) -> AppSettings:
    """
    Build settings by applying YAML defaults, then letting env / ``.env`` win.

    We set process environment for the demo; in real apps you rely on the shell.
    """
    yaml_defaults = load_yaml_mapping(yaml_path)
    for key, value in env.items():
        os.environ[key] = value
    cfg = SettingsConfigDict(
        env_prefix="APP_",
        env_file=str(env_file) if env_file else None,
        env_nested_delimiter="__",
        secrets_dir=str(secrets_dir) if secrets_dir else None,
        extra="ignore",
    )
    Dynamic = type("DynAppSettings", (AppSettings,), {"model_config": cfg})
    # kwargs seed defaults; env and env_file override per pydantic-settings rules.
    return Dynamic(**yaml_defaults)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        yml = root / "defaults.yaml"
        # YAML seeds nested defaults; leave ``environment`` to ``.env`` / process env.
        yml.write_text(
            yaml.dump({"db": {"host": "yaml-db", "port": 5000}}),
            encoding="utf-8",
        )
        dotenv = root / ".env"
        dotenv.write_text("APP_ENVIRONMENT=from-dotenv\n", encoding="utf-8")
        secrets = root / "secrets"
        secrets.mkdir()
        # File name matches the environment variable name used by pydantic-settings.
        (secrets / "APP_API_KEY").write_text("super-secret-from-file\n", encoding="utf-8")

        prior = {k: os.environ.pop(k, None) for k in ("APP_ENVIRONMENT", "APP_API_KEY")}
        try:
            s = settings_with_yaml_bootstrap(
                yaml_path=yml,
                env_file=dotenv,
                secrets_dir=secrets,
            )
            print("environment (from .env file):", s.environment)
            print("db host (from YAML bootstrap kwargs):", s.db.host)
            print("api_key from secrets_dir:", s.api_key.get_secret_value()[:8] + "...")
        finally:
            for key, val in prior.items():
                if val is not None:
                    os.environ[key] = val
                else:
                    os.environ.pop(key, None)


if __name__ == "__main__":
    main()
