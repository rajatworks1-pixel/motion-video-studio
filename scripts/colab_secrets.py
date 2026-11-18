#!/usr/bin/env python3
"""
Load secrets from Google Colab's userdata (secure secret storage).
Falls back to .env file for local development.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent

# Secret keys that should be loaded from Colab userdata
SECRET_KEYS = [
    "PIXABAY_API_KEY",
    "FREESOUND_API_KEY",
    "FREESOUND_CLIENT_ID",
    "PEXELS_API_KEY",
    "UNSPLASH_ACCESS_KEY",
    "ELEVENLABS_API_KEY",
    "NIM_API_KEY",
    "NIM_BASE_URL",
]


def load_colab_secrets() -> Dict[str, str]:
    """Load secrets from Google Colab's userdata."""
    secrets = {}
    try:
        from google.colab import userdata
        for key in SECRET_KEYS:
            try:
                value = userdata.get(key)
                if value:
                    secrets[key] = value
                    os.environ[key] = value
            except Exception:
                pass
        print(f"[colab_secrets] Loaded {len(secrets)} secrets from Colab userdata")
    except ImportError:
        print("[colab_secrets] Not running in Colab (google.colab not available)")
    except Exception as e:
        print(f"[colab_secrets] Error loading from userdata: {e}")
    return secrets


def load_dotenv() -> Dict[str, str]:
    """Load secrets from .env file (local development)."""
    secrets = {}
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        print(f"[colab_secrets] No .env file found at {env_path}")
        return secrets

    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key in SECRET_KEYS and value:
                        secrets[key] = value
                        os.environ[key] = value
        print(f"[colab_secrets] Loaded {len(secrets)} secrets from .env")
    except Exception as e:
        print(f"[colab_secrets] Error loading .env: {e}")
    return secrets


def get_secret(key: str, default: str = "") -> str:
    """Get a secret value, checking Colab userdata first, then .env, then environment."""
    # Priority: Colab userdata > .env > existing environment
    value = os.environ.get(key, default)
    return value


def setup_environment() -> Dict[str, str]:
    """Setup complete environment with all secrets loaded."""
    all_secrets = {}

    # Load from Colab userdata (highest priority in Colab)
    colab_secrets = load_colab_secrets()
    all_secrets.update(colab_secrets)

    # Load from .env (for local dev, doesn't override Colab)
    dotenv_secrets = load_dotenv()
    for k, v in dotenv_secrets.items():
        if k not in all_secrets:
            all_secrets[k] = v

    # Report status
    print("\n[secrets] Status:")
    for key in SECRET_KEYS:
        status = "✅" if all_secrets.get(key) else "⬜"
        print(f"  {status} {key}")

    missing = [k for k in SECRET_KEYS if not all_secrets.get(k)]
    if missing:
        print(f"\n[secrets] Warning: {len(missing)} secrets not set: {', '.join(missing)}")

    return all_secrets


if __name__ == "__main__":
    setup_environment()