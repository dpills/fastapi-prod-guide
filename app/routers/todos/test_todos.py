import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio
AUTH_HEADER = {"Authorization": "Bearer GOOD_TOKEN"}


async def test_create_todo(test_client: AsyncClient) -> None:
    """
    Test Creating a todo
    """
    # No Bearer Token
    r = await test_client.post("/v1/todos", json={"title": "test", "completed": False})
    assert r.status_code == 403

    # Invalid Bearer Token
    r = await test_client.post(
        "/v1/todos",
        json={"title": "test", "completed": False},
        headers={"Authorization": "Bearer BAD_TOKEN"},
    )
    assert r.status_code == 401

    # Valid Bearer Token
    r = await test_client.post(
        "/v1/todos",
        json={"title": "create_test", "completed": False},
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200
    assert r.json().get("id")


async def test_get_todos(test_client: AsyncClient) -> None:
    """
    Test Fetching todos
    """
    # Get all Todos
    r = await test_client.get("/v1/todos", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Get single Todo
    todo_id = results[0].get("id")
    r = await test_client.get(f"/v1/todos/{todo_id}", headers=AUTH_HEADER)
    assert r.status_code == 200

    # Unknown Todo ID
    r = await test_client.get("/v1/todos/652d729bb8da04810695a943", headers=AUTH_HEADER)
    assert r.status_code == 404


async def test_update_todo(test_client: AsyncClient) -> None:
    """
    Test updating a todo
    """
    # Get all Todos
    r = await test_client.get("/v1/todos", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Update a Todo
    todo_id = results[0].get("id")
    r = await test_client.put(
        f"/v1/todos/{todo_id}",
        json={"title": "update_test", "completed": True},
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    # Unknown Todo ID
    r = await test_client.put(
        "/v1/todos/652d729bb8da04810695a943",
        json={"title": "update_test", "completed": True},
        headers=AUTH_HEADER,
    )
    assert r.status_code == 404


async def test_delete_todo(test_client: AsyncClient) -> None:
    """
    Test deleting a todo
    """
    # Get all Todos
    r = await test_client.get("/v1/todos", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Delete a Todo
    todo_id = results[0].get("id")
    r = await test_client.delete(
        f"/v1/todos/{todo_id}",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    # Unknown Todo ID
    r = await test_client.delete(
        "/v1/todos/652d729bb8da04810695a943",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 404
