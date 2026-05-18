from unittest.mock import AsyncMock, patch


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_error_test(client):
    response = client.get("/error-test")
    assert response.status_code == 500


def test_create_and_list_items(client):
    response = client.post("/items", json={"name": "Libro", "description": "Un libro"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Libro"
    assert data["id"] is not None

    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_item_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404


def test_delete_item(client):
    create = client.post("/items", json={"name": "Borrar"})
    item_id = create.json()["id"]

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404


def test_pokemon(client):
    mock_data = {"id": 25, "name": "pikachu", "height": 4, "weight": 60}
    with patch(
        "app.services.pokemon_service.fetch_pokemon",
        new=AsyncMock(return_value=mock_data),
    ):
        response = client.get("/pokemon/pikachu")
    assert response.status_code == 200
    assert response.json()["name"] == "pikachu"
