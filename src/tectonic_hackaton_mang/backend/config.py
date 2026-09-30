"""Centrale paden en instellingen voor de backend."""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = BACKEND_DIR.parent
REPO_ROOT = PACKAGE_DIR.parents[1]

# Dataset en output staan in de repo-root (geen code).
DB_PATH = Path(os.environ.get("KBC_DB", REPO_ROOT / "data" / "fake.db"))
OUTPUT_DIR = Path(os.environ.get("KBC_OUTPUT", REPO_ROOT / "output"))
