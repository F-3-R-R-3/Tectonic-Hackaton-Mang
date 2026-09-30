from __future__ import annotations

import importlib
import json
import pkgutil

from . import signals
from .config import OUTPUT_DIR
from .data.connection import get_db


def _discover() -> list[tuple[str, object]]:
    """Verzamel alle functies uit ``signals/*.py`` via hun ``FUNCTIONS``-lijst."""
    found: list[tuple[str, object]] = []
    for module_info in pkgutil.iter_modules(signals.__path__):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{signals.__name__}.{module_info.name}")
        for func in getattr(module, "FUNCTIONS", []):
            found.append((module_info.name, func))
    return found


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    try:
        for module_name, func in _discover():
            result = func(conn)
            out_file = OUTPUT_DIR / f"{module_name}__{func.__name__}.json"
            out_file.write_text(
                json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"geschreven: {out_file.relative_to(OUTPUT_DIR.parent)}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
