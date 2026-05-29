from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response, status, Depends
from typing import List, Optional
from uuid import UUID
import os

from schemas.book import BookCreate, BookRead, BookStatus
from services.book_service import BookService
from repository.book_repository import BookRepositoryMemory, BookRepositoryDB
from db import AsyncSessionLocal, create_tables
from api.auth import router as auth_router
from api.deps import require_auth

USE_DB = os.getenv("USE_DB", "0") in ("1", "true", "True")
service: BookService = BookService(BookRepositoryMemory())


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    if USE_DB:
        await create_tables()
        session = AsyncSessionLocal()
        service = BookService(BookRepositoryDB(session=session))
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)


@app.get("/books", response_model=List[BookRead])
async def list_books(
    sort_by: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: int = 0,
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    _: str = Depends(require_auth),
):
    filters = {}
    if status is not None:
        filters["status"] = status
    if author is not None:
        filters["author"] = author
    return await service.get_books(sort_by=sort_by, limit=limit, offset=offset, **filters)


@app.get("/books/{book_id}", response_model=BookRead)
async def get_book(book_id: UUID, _: str = Depends(require_auth)):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(book_in: BookCreate, response: Response, _: str = Depends(require_auth)):
    book = await service.create_book(book_in)
    response.headers["Location"] = f"/books/{book.id}"
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, _: str = Depends(require_auth)):
    await service.delete_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)