"""Applicatie-kern: verbindt dataset, signalen en webserver.

Dit bestand bevat géén business-logica. Het importeert de bestaande modules
en orkestreert hun opstartvolgorde:

    generate (optioneel) ──► fake.db ──► export/signals ──► output/*.json
                                                      └──► FastAPI (:8000)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from .backend.config import DB_PATH, OUTPUT_DIR
from .backend.data.generate import generate as generate_dataset
from .backend.export import main as run_signal_export
from .backend.services import output_ready


@dataclass
class Application:
    """Hoofdmanager: connectielaag tussen data, signalen en API."""

    host: str = "127.0.0.1"
    port: int = 8000
    regenerate_db: bool = False
    skip_export: bool = False

    def ensure_dataset(self) -> None:
        """Zorg dat ``data/fake.db`` bestaat (of forceer hergeneratie)."""
        if self.regenerate_db or not DB_PATH.exists():
            print(f"Dataset genereren -> {DB_PATH}")
            counts = generate_dataset(DB_PATH)
            for table, n in counts.items():
                print(f"  {table:28} {n}")
        else:
            print(f"Dataset aanwezig: {DB_PATH}")

    def refresh_signals(self) -> None:
        """Draai alle signalen en schrijf ``output/*.json``."""
        print(f"Signalen exporteren -> {OUTPUT_DIR}")
        run_signal_export()

    def build_api(self):
        """Geef de FastAPI-app terug (zonder te starten)."""
        from .backend.api import create_app

        return create_app()

    def start_server(self) -> None:
        """Start de webserver (blokkeert)."""
        try:
            import uvicorn
        except ImportError as exc:
            raise SystemExit(
                "uvicorn/fastapi ontbreken. Installeer deps met: uv sync"
            ) from exc

        app = self.build_api()
        print(f"API luistert op http://{self.host}:{self.port}")
        print("  GET  /users")
        print("  GET  /users/{{id}}/signals")
        print("  POST /users/{{id}}/signals/{{sid}}/act")
        uvicorn.run(app, host=self.host, port=self.port, log_level="info")

    def bootstrap(self) -> None:
        """Dataset klaarzetten + signalen verversen (zonder server)."""
        self.ensure_dataset()
        if self.skip_export and output_ready():
            print(f"Export overgeslagen (bestaande output in {OUTPUT_DIR})")
            return
        self.refresh_signals()

    def run(self) -> None:
        """Volledige applicatie: data → signalen → webserver."""
        self.bootstrap()
        self.start_server()


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tectonic-hackaton-mang",
        description="KBC SignalEngine — start data, signalen en API.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind-adres voor de API (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Poort voor de API (default: 8000)",
    )
    parser.add_argument(
        "--regenerate-db",
        action="store_true",
        help="Forceer hergeneratie van data/fake.db",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Sla signaal-export over als output/*.json al bestaat",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Alleen dataset + signalen draaien, geen webserver",
    )
    parser.add_argument(
        "--serve-only",
        action="store_true",
        help="Alleen de API starten (geen generate/export)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """CLI-entrypoint: parse args en laat ``Application`` het werk verdelen."""
    args = _parse_args(argv)
    app = Application(
        host=args.host,
        port=args.port,
        regenerate_db=args.regenerate_db,
        skip_export=args.skip_export,
    )

    if args.serve_only:
        app.start_server()
        return

    if args.export_only:
        app.bootstrap()
        return

    app.run()


if __name__ == "__main__":
    main(sys.argv[1:])
