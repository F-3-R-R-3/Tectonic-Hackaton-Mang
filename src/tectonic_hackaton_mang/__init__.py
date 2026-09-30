"""Tectonic Hackathon 2026 — team Mang.

Python-package met de backend (``backend/``) en de website (``frontend/``).
"""


def main() -> None:
    """Entrypoint: start de applicatie-kern (data + signalen + API)."""
    from .main import main as run_app

    run_app()
