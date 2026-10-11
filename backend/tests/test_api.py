import groq
import httpx
import pytest
from fastapi.testclient import TestClient

from app import llm
from app.main import app

VALID_REPLY = '{"summary": "A short summary.", "tags": ["python", "web-apis", "testing"]}'


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client backed by a fresh SQLite file, with the real LLM call disabled."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def no_real_calls(client, text):
        raise AssertionError("Tests must not call the real Groq API")

    monkeypatch.setattr(llm, "_call_llm", no_real_calls)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def fake_llm(monkeypatch):
    """Make the LLM return (or raise) the given replies, in order."""
    calls = []

    def install(*replies):
        queue = list(replies)

        def fake_call(client, text):
            calls.append(text)
            reply = queue.pop(0)
            if isinstance(reply, Exception):
                raise reply
            return reply

        monkeypatch.setattr(llm, "_call_llm", fake_call)
        return calls

    return install


def test_create_then_list(client, fake_llm):
    fake_llm(VALID_REPLY)

    response = client.post("/entries", json={"text": "  Some text to summarize.  "})
    assert response.status_code == 201
    entry = response.json()
    assert entry["text"] == "Some text to summarize."
    assert entry["tags"] == ["python", "web-apis", "testing"]

    entries = client.get("/entries").json()
    assert [e["id"] for e in entries] == [entry["id"]]
    assert entries[0]["preview"] == "Some text to summarize."


def test_empty_text_is_rejected(client):
    assert client.post("/entries", json={"text": "   "}).status_code == 422


def test_too_long_text_is_rejected(client):
    assert client.post("/entries", json={"text": "x" * 5001}).status_code == 422


def test_malformed_then_valid_reply_succeeds(client, fake_llm):
    calls = fake_llm("not json", VALID_REPLY)
    assert client.post("/entries", json={"text": "Hello"}).status_code == 201
    assert len(calls) == 2


def test_malformed_twice_returns_502_and_saves_nothing(client, fake_llm):
    calls = fake_llm("not json", "still not json")
    response = client.post("/entries", json={"text": "Hello"})
    assert response.status_code == 502
    assert len(calls) == 2
    assert client.get("/entries").json() == []


def test_model_not_found_returns_502(client, fake_llm):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    fake_llm(
        groq.NotFoundError(
            "model not found", response=httpx.Response(404, request=request), body=None
        )
    )
    response = client.post("/entries", json={"text": "Hello"})
    assert response.status_code == 502
    assert response.json() == {"detail": "The configured AI model is unavailable."}


def test_unknown_entry_returns_404(client):
    assert client.get("/entries/999").status_code == 404
