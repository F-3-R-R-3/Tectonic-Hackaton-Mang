"""Authenticatie en autorisatie voor de website-API.

Eén login per demo-gezin. Wachtwoorden worden **nooit** als platte tekst
bewaard: bij het opstarten wordt per account een willekeurige salt gegenereerd
en het wachtwoord met PBKDF2-HMAC-SHA256 gehasht. Inloggen gebeurt met een
opaque sessietoken (``secrets.token_urlsafe``) dat na een TTL vervalt.

De server gebruikt ``user_for_token`` om te controleren dat een ingelogde klant
**enkel zijn eigen** signalen kan opvragen of acties kan uitvoeren
(IDOR-bescherming).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

PBKDF2_ITERATIONS = 200_000
SESSION_TTL = timedelta(hours=8)


@dataclass(frozen=True)
class Account:
    username: str
    password: str  # enkel om de hash te seeden, wordt nooit teruggegeven
    persona_id: str
    name: str
    persona_label: str


# Demo-gezinnen — ids 1..5 uit database.py (data/fake.db).
ACCOUNTS: list[Account] = [
    Account("emma.peeters", "Emma2026!", "p_1", "Emma Peeters", "Student"),
    Account("thomas.vermeulen", "Thomas2026!", "p_2", "Thomas Vermeulen", "Jonge starter"),
    Account("sofie.janssen", "Sofie2026!", "p_3", "Sofie Janssen", "Gezin met kinderen"),
    Account("lars.declercq", "Lars2026!", "p_4", "Lars Declercq", "Alleenstaande professional"),
    Account("marie.claeys", "Marie2026!", "p_5", "Marie Claeys", "Gepensioneerde"),
]


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)


class _Credentials:
    __slots__ = ("account", "salt", "digest")

    def __init__(self, account: Account) -> None:
        self.account = account
        self.salt = secrets.token_bytes(16)
        self.digest = _hash(account.password, self.salt)


# username -> credentials (met per-account salt)
_CREDENTIALS: dict[str, _Credentials] = {a.username: _Credentials(a) for a in ACCOUNTS}

# token -> {username, expires}
_SESSIONS: dict[str, dict] = {}


def authenticate(username: str, password: str) -> str | None:
    """Controleer de login en geef een sessietoken terug (of ``None``)."""
    creds = _CREDENTIALS.get(username)
    if creds is None:
        # Doe toch een hash-vergelijking om timing-aanvallen te dempen.
        _hash(password, b"dummy-salt")
        return None
    candidate = _hash(password, creds.salt)
    if not hmac.compare_digest(candidate, creds.digest):
        return None
    token = secrets.token_urlsafe(32)
    _SESSIONS[token] = {
        "username": username,
        "expires": datetime.now(tz=UTC) + SESSION_TTL,
    }
    return token


def user_for_token(token: str | None) -> Account | None:
    """Geef het account van een geldig token, of ``None``."""
    if not token:
        return None
    session = _SESSIONS.get(token)
    if session is None:
        return None
    if session["expires"] < datetime.now(tz=UTC):
        _SESSIONS.pop(token, None)
        return None
    creds = _CREDENTIALS.get(session["username"])
    return creds.account if creds else None


def revoke(token: str | None) -> None:
    if token:
        _SESSIONS.pop(token, None)


def public_account(account: Account) -> dict:
    """Accountinfo zonder gevoelige velden (voor de front-end)."""
    return {
        "username": account.username,
        "persona_id": account.persona_id,
        "name": account.name,
        "persona_label": account.persona_label,
    }


def demo_logins() -> list[dict]:
    """Publieke login-hints voor de demo (zonder hash)."""
    return [
        {"username": a.username, "name": a.name, "persona_label": a.persona_label}
        for a in ACCOUNTS
    ]
