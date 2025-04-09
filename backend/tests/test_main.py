
def test_base_request(client):
    response = client.get("/")
    assert response.status_code == 200

def test_latest_detections(client):
    response = client.get("/latest-detections")
    body = response.json()
    assert response.status_code == 200
    