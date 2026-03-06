from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response, status, Depends
from typing import Optional, AsyncGenerator
from uuid import UUID

from schemas.book import BookCreate, BookRead, BookStatus, BookListResponse
from services.book_service import BookService
from repository.book_repository import BookRepository
from sqlalchemy.ext.asyncio import AsyncSession
from db import AsyncSessionLocal, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_service(
    session: AsyncSession = Depends(get_session),
) -> BookService:
    repo = BookRepository(session=session)
    return BookService(repo)


@app.get("/books", response_model=BookListResponse)
async def list_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: Optional[int] = 10,
    service: BookService = Depends(get_service),
):
    books, next = await service.get_books(
        status=status,
        author=author,
        sort_by=sort_by,
        cursor=cursor,
        limit=limit,
    )

    return {"count": len(books), "next": next, "result": books}


@app.get("/books/{book_id}", response_model=BookRead)
async def get_book(book_id: UUID, service: BookService = Depends(get_service)):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate, response: Response, service: BookService = Depends(get_service)
):
    book = await service.create_book(book_in)
    response.headers["Location"] = f"/books/{book.id}"
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, service: BookService = Depends(get_service)):
    # idempotent delete: always return 204
    await service.delete_book(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
