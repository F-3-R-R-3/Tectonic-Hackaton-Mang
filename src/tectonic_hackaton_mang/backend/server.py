"""Kleine JSON-API voor de React-website (dependency-vrij, stdlib only).

Serveert het SignalEngine-contract dat ``website_api.build_personas`` uit de
echte dataset + functies bouwt, **achter een login**. Elke klant ziet enkel zijn
eigen signalen (autorisatie-check voorkomt IDOR).

Endpoints:
    GET  /api/health                         (publiek)
    GET  /api/auth/demo-logins               (publiek, login-hints voor de demo)
    POST /api/auth/login                     {username, password} -> {token, user}
    POST /api/auth/logout                    (Bearer token)
    GET  /api/me                             (Bearer token) -> eigen persona + signalen
    GET  /api/users/{persona_id}/signals     (Bearer token, enkel eigen id)
    POST /api/users/{persona_id}/signals/{signal_id}/act  (Bearer token, enkel eigen id)

Gebruik:
    uv run python -m tectonic_hackaton_mang.backend.server --port 8000
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .auth import (
    authenticate,
    demo_logins,
    public_account,
    revoke,
    user_for_token,
)
from .data.connection import get_db
from .website_api import build_personas

# In-memory cache zodat we de functies niet bij elk request opnieuw draaien.
_CACHE: dict | None = None


def _payload() -> dict:
    global _CACHE
    if _CACHE is None:
        conn = get_db()
        try:
            _CACHE = build_personas(conn)
        finally:
            conn.close()
    return _CACHE


def _persona(persona_id: str) -> dict | None:
    for p in _payload()["personas"]:
        if p["id"] == persona_id or str(p.get("customer_id")) == persona_id:
            return p
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "KBCSignalEngine/0.1"

    # --- helpers -----------------------------------------------------------
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _error(self, status: int, message: str) -> None:
        self._send(status, {"error": message})

    def _token(self) -> str | None:
        header = self.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            return header[7:].strip()
        return None

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return {}

    # --- routing -----------------------------------------------------------
    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(204, {})

    def do_GET(self) -> None:  # noqa: N802
        parts = [p for p in self.path.split("?")[0].split("/") if p]
        try:
            if parts == ["api", "health"]:
                meta = _payload()["meta"]
                self._send(200, {"status": "ok", **meta})
                return
            if parts == ["api", "auth", "demo-logins"]:
                self._send(200, {"accounts": demo_logins()})
                return
            if parts == ["api", "me"]:
                account = user_for_token(self._token())
                if account is None:
                    self._error(401, "Niet ingelogd")
                    return
                persona = _persona(account.persona_id)
                if persona is None:
                    self._error(404, "Persona niet gevonden")
                    return
                self._send(200, {"user": public_account(account), "persona": persona})
                return
            if len(parts) == 4 and parts[:2] == ["api", "users"] and parts[3] == "signals":
                account = user_for_token(self._token())
                if account is None:
                    self._error(401, "Niet ingelogd")
                    return
                if parts[2] not in (account.persona_id,):
                    self._error(403, "Geen toegang tot deze klant")
                    return
                persona = _persona(parts[2])
                if persona is None:
                    self._error(404, "Persona niet gevonden")
                    return
                self._send(200, {"signals": persona["signals"], "persona": persona})
                return
            self._error(404, "Onbekend endpoint")
        except Exception as exc:  # noqa: BLE001
            self._error(500, str(exc))

    def do_POST(self) -> None:  # noqa: N802
        parts = [p for p in self.path.split("?")[0].split("/") if p]
        try:
            if parts == ["api", "auth", "login"]:
                body = self._read_json()
                token = authenticate(str(body.get("username", "")), str(body.get("password", "")))
                if token is None:
                    self._error(401, "Onjuiste gebruikersnaam of wachtwoord")
                    return
                account = user_for_token(token)
                self._send(200, {"token": token, "user": public_account(account)})
                return
            if parts == ["api", "auth", "logout"]:
                revoke(self._token())
                self._send(200, {"status": "ok"})
                return
            if len(parts) == 6 and parts[:2] == ["api", "users"] and parts[5] == "act":
                account = user_for_token(self._token())
                if account is None:
                    self._error(401, "Niet ingelogd")
                    return
                if parts[2] != account.persona_id:
                    self._error(403, "Geen toegang tot deze klant")
                    return
                persona = _persona(parts[2])
                if persona is None:
                    self._error(404, "Persona niet gevonden")
                    return
                signal = next((s for s in persona["signals"] if s["id"] == parts[4]), None)
                if signal is None:
                    self._error(404, "Signaal niet gevonden")
                    return
                body = self._read_json()
                action = body.get("action_type") or signal["solution"]["action_type"]
                self._send(
                    200,
                    {
                        "status": "opgelost",
                        "signal_id": signal["id"],
                        "action_type": action,
                        "message": f"Actie '{action}' uitgevoerd voor signaal {signal['id']}.",
                    },
                )
                return
            self._error(404, "Onbekend endpoint")
        except Exception as exc:  # noqa: BLE001
            self._error(500, str(exc))

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="KBC SignalEngine JSON-API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    meta = _payload()["meta"]
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        f"KBC SignalEngine API op http://{args.host}:{args.port} "
        f"({meta['customer_count']} klanten, {meta['signal_count']} signalen)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGestopt.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
