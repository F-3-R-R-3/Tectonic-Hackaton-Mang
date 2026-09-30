"""Tectonic Hackathon 2026 — team Mang.

Python-package met de backend (``backend/``) en de website (``frontend/``).
"""


def main() -> None:
    """Entrypoint: draai alle signalen en schrijf de JSON-output voor de website."""
    from .backend.export import main as run_export

    run_export()
