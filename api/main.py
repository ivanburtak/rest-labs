from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response, status
from typing import List, Optional
from uuid import UUID
import os

from schemas.book import BookCreate, BookRead, BookStatus
from services.book_service import BookService
from repository.book_repository import BookRepositoryMemory, BookRepositoryDB
from db import AsyncSessionLocal, create_tables


# choose repository by env var; default is in-memory repository used by BookService()
USE_DB = os.getenv("USE_DB", "0") in ("1", "true", "True")

# Initialize service with in-memory repository by default
# The lifespan context manager will override this if USE_DB is True
service: BookService = BookService(BookRepositoryMemory())


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    if USE_DB:
        # ensure tables exist
        await create_tables()
        # create a session for the DB-backed repository
        session = AsyncSessionLocal()
        repo = BookRepositoryDB(session=session)
        service = BookService(repo)
    # else: service is already initialized with BookRepositoryMemory at module level
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/books", response_model=List[BookRead])
async def list_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: int = 0,
):
    """Get all books with optional filtering by status and author, sorting, and limit-offset pagination."""
    books = await service.get_books(
        status=status, author=author, sort_by=sort_by, limit=limit, offset=offset
    )
    return books


@app.get("/books/{book_id}", response_model=BookRead)
async def get_book(book_id: UUID):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(book_in: BookCreate, response: Response):
    book = await service.create_book(book_in)
    response.headers["Location"] = f"/books/{book.id}"
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    # idempotent delete: always return 204
    await service.delete_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
