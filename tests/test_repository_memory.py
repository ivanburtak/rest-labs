"""Tests for in-memory repository"""

import pytest
from uuid import uuid4

from repository.book_repository import BookRepositoryMemory
from models import data


@pytest.fixture(autouse=True)
def clear_data():
    """Clear in-memory storage before each test"""
    data.BOOKS.clear()
    yield


@pytest.mark.asyncio
async def test_repo_add_and_get():
    """Test adding and retrieving from in-memory repository"""
    repo = BookRepositoryMemory()

    book = {
        "id": str(uuid4()),
        "title": "Test Book",
        "author": "Test Author",
        "description": "A test",
        "status": "available",
        "year": 2020,
    }

    # Add
    result = await repo.add(book)
    assert result["id"] == book["id"]

    # Get
    retrieved = await repo.get_by_id(book["id"])
    assert retrieved is not None
    assert retrieved["title"] == "Test Book"


@pytest.mark.asyncio
async def test_repo_list_all():
    """Test listing all books from in-memory repository"""
    repo = BookRepositoryMemory()

    # Add books
    for i in range(3):
        book = {
            "id": str(uuid4()),
            "title": f"Book {i}",
            "author": "Author",
            "description": None,
            "status": "available",
            "year": 2020,
        }
        await repo.add(book)

    # List all
    books = await repo.list_all()
    assert len(books) == 3


@pytest.mark.asyncio
async def test_repo_delete():
    """Test deleting from in-memory repository"""
    repo = BookRepositoryMemory()

    book_id = str(uuid4())
    book = {
        "id": book_id,
        "title": "To Delete",
        "author": "Author",
        "description": None,
        "status": "available",
        "year": 2020,
    }

    # Add
    await repo.add(book)

    # Verify exists
    retrieved = await repo.get_by_id(book_id)
    assert retrieved is not None

    # Delete
    deleted = await repo.delete_by_id(book_id)
    assert deleted is True

    # Verify gone
    retrieved = await repo.get_by_id(book_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_repo_delete_nonexistent():
    """Test delete returns False for non-existent book"""
    repo = BookRepositoryMemory()

    fake_id = str(uuid4())
    deleted = await repo.delete_by_id(fake_id)
    assert deleted is False
