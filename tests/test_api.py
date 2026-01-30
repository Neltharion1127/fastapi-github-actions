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