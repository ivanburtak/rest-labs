"""Integration tests for database-backed repository"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models.orm import Base, Book as BookORM
from repository.book_repository import BookRepositoryDB
from uuid import uuid4


@pytest_asyncio.fixture
async def test_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_db_repo_add_and_get(test_db):
    repo = BookRepositoryDB(test_db)

    book_id = str(uuid4())
    book_dict = {
        "id": book_id,
        "title": "Test Book",
        "author": "Test Author",
        "description": "A test book",
        "status": "available",
        "year": 2020,
    }

    result = await repo.add(book_dict)
    assert result["id"] == book_id
    assert result["title"] == "Test Book"

    retrieved = await repo.get_by_id(book_id)
    assert retrieved is not None
    assert retrieved["title"] == "Test Book"
    assert retrieved["author"] == "Test Author"


@pytest.mark.asyncio
async def test_db_repo_list_all(test_db):
    repo = BookRepositoryDB(test_db)

    for i in range(3):
        book_dict = {
            "id": str(uuid4()),
            "title": f"Book {i}",
            "author": "Author",
            "description": None,
            "status": "available",
            "year": 2020,
        }
        await repo.add(book_dict)

    books = await repo.list_all()
    assert len(books) == 3
    assert all(b["title"].startswith("Book") for b in books)


@pytest.mark.asyncio
async def test_db_repo_delete(test_db):
    repo = BookRepositoryDB(test_db)

    book_id = str(uuid4())
    book_dict = {
        "id": book_id,
        "title": "To Delete",
        "author": "Author",
        "description": None,
        "status": "available",
        "year": 2020,
    }

    await repo.add(book_dict)

    retrieved = await repo.get_by_id(book_id)
    assert retrieved is not None

    deleted = await repo.delete_by_id(book_id)
    assert deleted is True

    retrieved = await repo.get_by_id(book_id)
    assert retrieved is None

    deleted = await repo.delete_by_id(book_id)
    assert deleted is False


@pytest.mark.asyncio
async def test_db_repo_delete_nonexistent(test_db):
    repo = BookRepositoryDB(test_db)

    fake_id = str(uuid4())
    deleted = await repo.delete_by_id(fake_id)
    assert deleted is False


@pytest.mark.asyncio
async def test_db_repo_get_nonexistent(test_db):
    repo = BookRepositoryDB(test_db)

    fake_id = str(uuid4())
    retrieved = await repo.get_by_id(fake_id)
    assert retrieved is None
