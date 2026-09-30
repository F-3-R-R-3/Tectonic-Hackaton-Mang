"""Dunne FastAPI-laag: routes alleen, logica leeft in ``services``."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import services


class ActRequest(BaseModel):
    action_type: str = Field(..., min_length=1)


def create_app() -> FastAPI:
    """Bouw de API die de React-frontend verwacht."""
    app = FastAPI(
        title="KBC SignalEngine",
        description="Signaal ➔ Probleem ➔ Oplossing API voor de hackathon-demo.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/users")
    def get_users() -> list[dict]:
        return services.list_users(demo_only=True)

    @app.get("/users/{user_id}/signals")
    def get_signals(user_id: str) -> list[dict]:
        try:
            return services.list_signals_for_user(user_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Ongeldige user id: {user_id}") from exc

    @app.post("/users/{user_id}/signals/{signal_id}/act")
    def act_on_signal(user_id: str, signal_id: str, body: ActRequest) -> dict[str, str]:
        try:
            return services.perform_action(user_id, signal_id, body.action_type)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app
