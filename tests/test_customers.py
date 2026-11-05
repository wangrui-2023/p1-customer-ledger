from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_page_opens(client: TestClient) -> None:
    response = client.get("/customers")
    assert response.status_code == 200
    assert "客户台账" in response.text


def test_create_then_search(client: TestClient) -> None:
    response = client.post(
        "/customers",
        data={
            "name": "测试客户",
            "phone": "13800000000",
            "company": "测试公司",
            "note": "来自验收测试",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/customers"

    listing = client.get("/customers")
    assert "测试客户" in listing.text

    search = client.get("/customers", params={"q": "测试客户"})
    assert "测试客户" in search.text


def test_validation_error_renders_form(client: TestClient) -> None:
    response = client.post(
        "/customers",
        data={"name": " ", "phone": "abc", "company": "", "note": ""},
        follow_redirects=False,
    )
    assert response.status_code == 422
    assert "姓名必填" in response.text
    assert "手机号只能包含数字" in response.text
    assert "还没有客户记录" not in response.text

    listing = client.get("/customers")
    assert "还没有客户记录" in listing.text


def test_data_survives_restart(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "persist.db"))

    with TestClient(app) as first_client:
        response = first_client.post(
            "/customers",
            data={"name": "持久客户", "phone": "", "company": "", "note": ""},
            follow_redirects=False,
        )
        assert response.status_code == 303

    with TestClient(app) as second_client:
        listing = second_client.get("/customers")
        assert "持久客户" in listing.text
