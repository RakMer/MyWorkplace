import pytest
import app as flask_app


@pytest.fixture()
def client(monkeypatch):
    # Spark init'i sahtelemek için stub döndür.
    monkeypatch.setattr(flask_app, "init_spark", lambda: ("spark", "df"))
    app = flask_app.app
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_api_articles_success(monkeypatch, client):
    sample_articles = [
        {"title": "AI News", "author": "pg", "points": 100, "created_at": "2025-01-01T10:00:00"},
        {"title": "DB Update", "author": "alice", "points": 80, "created_at": "2025-01-02T12:00:00"},
    ]
    monkeypatch.setattr(flask_app, "query_articles", lambda df, **_: sample_articles)

    resp = client.get("/api/articles?keyword=ai&author=pg&sort=date_desc&limit=2")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["success"] is True
    assert data["count"] == 2
    assert data["data"] == sample_articles


def test_api_statistics_success(monkeypatch, client):
    monkeypatch.setattr(
        flask_app,
        "query_statistics",
        lambda df: {"total": 10, "with_author": 8},
    )

    resp = client.get("/api/statistics")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["success"] is True
    assert data["data"] == {"total": 10, "with_author": 8}
