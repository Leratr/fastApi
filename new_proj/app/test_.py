from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_ram_info():
    response = client.get("/ram")
    assert response.status_code == 200
    assert "total" in response.json()
    assert "available" in response.json()
    assert "used" in response.json()
    assert "percent" in response.json()

def test_get_memory_info():
    response = client.get("/memory")
    assert response.status_code == 200
    assert "total" in response.json()
    assert "used" in response.json()
    assert "free" in response.json()
    assert "percent" in response.json()

def test_get_swap_info():
    response = client.get("/swap")
    assert response.status_code == 200
    assert "total" in response.json()
    assert "used" in response.json()
    assert "free" in response.json()
    assert "percent" in response.json()

def test_get_disk_info():
    response = client.get("/disk")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_get_network_info():
    response = client.get("/network")
    assert response.status_code == 200
    assert "bytes_sent" in response.json()
    assert "bytes_received" in response.json()
    assert "packets_sent" in response.json()
    assert "packets_received" in response.json()

def test_get_connections():
    response = client.get("/connections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_temperature_info():
    response = client.get("/temperature")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
