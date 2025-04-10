import os

def test_base_request(client):
    response = client.get("/")
    assert response.status_code == 200

def test_empty_detections(client):
    response = client.get("/latest-detections")
    assert response.status_code == 200
    body = response.json()
    assert body == []

def test_missing_image(client):
    response = client.get(
        "/smile-image",
        params={"id": 999}
    )
    assert response.status_code == 404
    
def test_detection(client):
    image_name = "test_smile.jpg"
    image_path = os.path.join("tests", image_name)
    test_coords = {
        "x": 439,
        "y": 359,
        "w": 104,
        "h": 52
    }

    with open(image_path, "rb") as image_file:
        response = client.post(
            "/detect-smile",
            files={"file": (image_name, image_file, "image/jpg")}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["coordinates"] == test_coords
    id = body["id"]

    response = client.get("/latest-detections")
    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == id

    response = client.get(
        "/smile-image",
        params={"id": id}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0