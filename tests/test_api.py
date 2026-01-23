# @Time: 1/23/26 20:51
# @Author: jie
# @File: test_api.py.py
# @Description:
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_hello_default():
    resp = client.get("/hello")
    assert resp.status_code == 200
    assert resp.json() == {"message": "hello world"}

def test_hello_name():
    resp = client.get("/hello?name=Jie")
    assert resp.status_code == 200
    assert resp.json() == {"message": "hello Jie"}

def test_metrics_shape():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()

    assert "uptime_seconds" in data
    assert "request_count" in data
    assert isinstance(data["uptime_seconds"], int)
    assert isinstance(data["request_count"], int)
    assert data["uptime_seconds"] >= 0
    assert data["request_count"] >= 1