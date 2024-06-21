from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_rates():
    response = client.get("/rates?base_currency=USD")
    assert response.status_code == 200
    assert "USD" in response.json()


def test_convert():
    response = client.get("/convert?amount=100&from_currency=USD&to_currency=EUR")
    assert response.status_code == 200
    assert "amount" in response.json()
