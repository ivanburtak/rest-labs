import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from models import data
from schemas.book import BookStatus


@pytest.fixture(autouse=True)
def clear_data():
    # clean in-memory storage before each test
    data.BOOKS.clear()
    yield


@pytest.mark.asyncio
async def test_create_and_get_book():
    payload = {
        "title": "Test Book",
        "author": "Author A",
        "description": "Desc",
        "status": "available",
        "year": 2000,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json=payload)
        assert r.status_code == 201
        created = r.json()
        assert created["title"] == payload["title"]

        # get by id
        bid = created["id"]
        r2 = await ac.get(f"/books/{bid}")
        assert r2.status_code == 200
        assert r2.json()["id"] == bid


@pytest.mark.asyncio
async def test_list_filters_and_sorting():
    books = [
        {
            "title": "B Title",
            "author": "Alice",
            "description": "x",
            "status": "available",
            "year": 1999,
        },
        {
            "title": "A Title",
            "author": "Bob",
            "description": "y",
            "status": "issued",
            "year": 2005,
        },
        {
            "title": "C Title",
            "author": "Alice",
            "description": "z",
            "status": "available",
            "year": 2010,
        },
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for b in books:
            r = await ac.post("/books", json=b)
            assert r.status_code == 201

        # filter by author
        r = await ac.get("/books", params={"author": "alice"})
        assert r.status_code == 200
        res = r.json()
        assert len(res) == 2

        # filter by status
        r = await ac.get("/books", params={"status": "issued"})
        assert r.status_code == 200
        res = r.json()
        assert len(res) == 1

        # sort by title
        r = await ac.get("/books", params={"sort_by": "title"})
        assert r.status_code == 200
        res = r.json()
        titles = [b["title"] for b in res]
        assert titles == sorted(titles)

        # sort by year
        r = await ac.get("/books", params={"sort_by": "year"})
        res = r.json()
        years = [b["year"] for b in res]
        assert years == sorted(years)


@pytest.mark.asyncio
async def test_delete_idempotent():
    payload = {
        "title": "To Delete",
        "author": "X",
        "description": "d",
        "status": "available",
        "year": 2020,
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json=payload)
        bid = r.json()["id"]

        # first delete
        r1 = await ac.delete(f"/books/{bid}")
        assert r1.status_code == 204

        # second delete should also be 204 (idempotent)
        r2 = await ac.delete(f"/books/{bid}")
        assert r2.status_code == 204


@pytest.mark.asyncio
async def test_validation_error():
    # missing title
    payload = {"author": "X", "description": "d", "status": "available", "year": 2020}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json=payload)
        assert r.status_code == 422
