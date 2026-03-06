import pytest
from schemas.book import BookStatus
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_book(client: AsyncClient):
    book_data = {
        "title": "Test Book",
        "author": "Alice",
        "year": 2023,
        "status": BookStatus.issued,
    }

    response = await client.post("/books", json=book_data)
    assert response.status_code == 201
    created = response.json()
    book_id = created["id"]
    assert created["title"] == "Test Book"

    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == book_id
    assert fetched["title"] == "Test Book"

    response = await client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert any(b["id"] == book_id for b in data["result"])

    response = await client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_books_with_filters_and_sort(client: AsyncClient):
    # Create multiple books
    books = [
        {
            "title": "Book A",
            "author": "Alice",
            "year": 2021,
            "status": BookStatus.issued,
        },
        {
            "title": "Book B",
            "author": "Bob",
            "year": 2022,
            "status": BookStatus.available,
        },
        {
            "title": "Book C",
            "author": "Alice",
            "year": 2023,
            "status": BookStatus.issued,
        },
    ]
    for book in books:
        await client.post("/books", json=book)

    response = await client.get("/books", params={"author": "Alice", "limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert all(b["author"] == "Alice" for b in data["result"])
    assert len(data["result"]) == 2

    first_page = await client.get("/books", params={"limit": 2})
    first_data = first_page.json()
    next_cursor = first_data["next"]
    if next_cursor:
        second_page = await client.get(
            "/books", params={"cursor": next_cursor, "limit": 2}
        )
        second_data = second_page.json()
        # Ensure no duplicates between pages
        ids_first = {b["id"] for b in first_data["result"]}
        ids_second = {b["id"] for b in second_data["result"]}
        assert ids_first.isdisjoint(ids_second)


@pytest.mark.asyncio
async def test_cursor_pagination(client: AsyncClient):
    # create 5 books
    for i in range(1, 6):
        await client.post(
            "/books",
            json={
                "title": f"Book {i}",
                "author": "Author",
                "year": 2000 + i,
                "status": BookStatus.available,
            },
        )

    # first page
    response = await client.get("/books", params={"limit": 2})
    data = response.json()
    print(data)
    first_page_ids = [b["id"] for b in data["result"]]
    next_cursor = data["next"]
    assert len(first_page_ids) == 2
    assert next_cursor is not None

    # second page
    response = await client.get("/books", params={"cursor": next_cursor, "limit": 2})
    data = response.json()
    second_page_ids = [b["id"] for b in data["result"]]
    assert len(second_page_ids) == 2
    # Ensure no overlap
    assert set(first_page_ids).isdisjoint(second_page_ids)

    # last page (remaining)
    next_cursor = data["next"]
    response = await client.get("/books", params={"cursor": next_cursor, "limit": 2})
    data = response.json()
    last_page_ids = [b["id"] for b in data["result"]]
    assert len(last_page_ids) == 1  # remaining book
    # Ensure no overlap
    assert set(first_page_ids).isdisjoint(last_page_ids)
    assert set(second_page_ids).isdisjoint(last_page_ids)
