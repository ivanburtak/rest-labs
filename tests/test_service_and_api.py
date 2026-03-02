import pytest
from models import data
from schemas.book import BookStatus, BookCreate
from services.book_service import BookService
from repository.book_repository import BookRepositoryMemory


@pytest.fixture(autouse=True)
def clear_data():
    """Clear in-memory storage before each test"""
    data.BOOKS.clear()
    yield


# ============ SERVICE LAYER TESTS ============


@pytest.mark.asyncio
async def test_service_create_and_get():
    service = BookService(BookRepositoryMemory())

    book_in = BookCreate(title="Test", author="A", year=2000)
    created = await service.create_book(book_in)
    assert created.title == "Test"
    assert created.id is not None

    retrieved = await service.get_book(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_service_pagination():
    service = BookService(BookRepositoryMemory())

    for i in range(10):
        book_in = BookCreate(title=f"Book {i}", author="Author", year=2000 + i)
        await service.create_book(book_in)

    page1 = await service.get_books(limit=5, offset=0)
    assert len(page1) == 5

    page2 = await service.get_books(limit=5, offset=5)
    assert len(page2) == 5

    all_books = await service.get_books(limit=None, offset=0)
    assert len(all_books) == 10

    empty = await service.get_books(limit=5, offset=20)
    assert len(empty) == 0


@pytest.mark.asyncio
async def test_service_filters_with_pagination():
    service = BookService(BookRepositoryMemory())

    for i in range(6):
        status = "available" if i % 2 == 0 else "issued"
        book_in = BookCreate(
            title=f"Book {i}", author="Author", year=2000, status=status
        )
        await service.create_book(book_in)

    available = await service.get_books(status=BookStatus.available, limit=2, offset=0)
    assert len(available) == 2
    assert all(b.status == BookStatus.available for b in available)


@pytest.mark.asyncio
async def test_service_sorting():
    service = BookService(BookRepositoryMemory())

    books_data = [
        ("Z Title", 2000),
        ("A Title", 2005),
        ("M Title", 1990),
    ]

    for title, year in books_data:
        book_in = BookCreate(title=title, author="Author", year=year)
        await service.create_book(book_in)

    by_title = await service.get_books(sort_by="title")
    titles = [b.title for b in by_title]
    assert titles == ["A Title", "M Title", "Z Title"]

    by_year = await service.get_books(sort_by="year")
    years = [b.year for b in by_year]
    assert years == [1990, 2000, 2005]


@pytest.mark.asyncio
async def test_service_delete_idempotent():
    service = BookService(BookRepositoryMemory())

    book_in = BookCreate(title="To Delete", author="A", year=2000)
    created = await service.create_book(book_in)

    await service.delete_book(created.id)

    retrieved = await service.get_book(created.id)
    assert retrieved is None

    # delete again (idempotent - should not raise)
    await service.delete_book(created.id)


# ============ API LAYER TESTS ============

from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from api.main import app


@pytest.mark.asyncio
async def test_api_create_and_get_book():
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
        assert "Location" in r.headers

        created = r.json()
        assert created["title"] == payload["title"]

        # get by id
        bid = created["id"]
        r2 = await ac.get(f"/books/{bid}")
        assert r2.status_code == 200
        assert r2.json()["id"] == bid


@pytest.mark.asyncio
async def test_api_list_with_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for i in range(12):
            payload = {
                "title": f"Book {i:02d}",
                "author": "Author",
                "status": "available",
                "year": 2000 + i,
            }
            r = await ac.post("/books", json=payload)
            assert r.status_code == 201

        r = await ac.get("/books")
        assert r.status_code == 200
        books = r.json()
        assert len(books) == 10

        r = await ac.get("/books", params={"limit": 5})
        assert r.status_code == 200
        books = r.json()
        assert len(books) == 5

        r = await ac.get("/books", params={"limit": 5, "offset": 5})
        assert r.status_code == 200
        books = r.json()
        assert len(books) == 5

        # test offset beyond data
        r = await ac.get("/books", params={"limit": 5, "offset": 20})
        assert r.status_code == 200
        books = r.json()
        assert len(books) == 0


@pytest.mark.asyncio
async def test_api_filters_and_sorting():
    books_data = [
        {"title": "B Title", "author": "Alice", "status": "available", "year": 1999},
        {"title": "A Title", "author": "Bob", "status": "issued", "year": 2005},
        {"title": "C Title", "author": "Alice", "status": "available", "year": 2010},
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for b in books_data:
            r = await ac.post("/books", json=b)
            assert r.status_code == 201

        # filter by author (don't pass limit=None, use default)
        r = await ac.get("/books", params={"author": "Alice"})
        assert r.status_code == 200
        result = r.json()
        assert len(result) == 2

        # filter by status
        r = await ac.get("/books", params={"status": "issued"})
        assert r.status_code == 200
        result = r.json()
        assert len(result) == 1

        # sort by title
        r = await ac.get("/books", params={"sort_by": "title"})
        assert r.status_code == 200
        result = r.json()
        titles = [b["title"] for b in result]
        assert titles == sorted(titles)

        # sort by year
        r = await ac.get("/books", params={"sort_by": "year"})
        result = r.json()
        years = [b["year"] for b in result]
        assert years == sorted(years)


@pytest.mark.asyncio
async def test_api_delete_idempotent():
    payload = {"title": "To Delete", "author": "X", "status": "available", "year": 2020}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json=payload)
        bid = r.json()["id"]

        r1 = await ac.delete(f"/books/{bid}")
        assert r1.status_code == 204

        # second delete should also be 204 (idempotent)
        r2 = await ac.delete(f"/books/{bid}")
        assert r2.status_code == 204


@pytest.mark.asyncio
async def test_api_validation_error():
    payload = {"author": "X", "status": "available", "year": 2020}  # missing title
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/books", json=payload)
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_api_get_nonexistent_book():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        fake_id = str(uuid4())
        r = await ac.get(f"/books/{fake_id}")
        assert r.status_code == 404
