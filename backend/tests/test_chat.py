
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.api import routes

client = TestClient(app)


def test_chat_success(monkeypatch):
    # Replace the real AI call with a predictable mock response.
    mock_send_message = AsyncMock(return_value="Python is a programming language.")
    monkeypatch.setattr(
        routes.chat_service,
        "send_message",
        mock_send_message,
    )

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is Python?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "reply": "Python is a programming language.",
        "model": routes.settings.gemini_model,
    }

    mock_send_message.assert_awaited_once_with("What is Python?")


def test_chat_empty_message():
    response = client.post(
        "/api/v1/chat",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_chat_missing_message():
    response = client.post(
        "/api/v1/chat",
        json={},
    )

    assert response.status_code == 422


def test_chat_message_too_long():
    response = client.post(
        "/api/v1/chat",
        json={"message": "a" * 10001},
    )

    assert response.status_code == 422


def test_chat_service_failure(monkeypatch):
    mock_send_message = AsyncMock(
        side_effect=RuntimeError("Gemini service unavailable")
    )
    monkeypatch.setattr(
        routes.chat_service,
        "send_message",
        mock_send_message,
    )

    response = client.post(
        "/api/v1/chat",
        json={"message": "Explain APIs"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "The AI service could not complete the request."
    }