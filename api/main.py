from fastapi import Depends, FastAPI, HTTPException, Response, status as http_status
from typing import List, Optional
from uuid import UUID
from schemas.book import BookCreate, BookRead, BookStatus
from services.book_service import BookService
from repository.book_repository import BookRepository
from db import get_db


app = FastAPI()


async def get_service(db=Depends(get_db)):
    repo = BookRepository(db)
    return BookService(repo)


@app.get("/books", response_model=List[BookRead])
async def list_books(
    sort_by: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: int = 0,
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    service: BookService = Depends(get_service),
):
    filters = {}
    if status is not None:
        filters["status"] = status
    if author is not None:
        filters["author"] = author

    books = await service.get_books(
        sort_by=sort_by, limit=limit, offset=offset, status=status, author=author
    )
    return books


@app.get("/books/{book_id}", response_model=BookRead)
async def get_book(
    book_id: UUID,
    service: BookService = Depends(get_service),
):
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@app.post("/books", response_model=BookRead, status_code=http_status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    response: Response,
    service: BookService = Depends(get_service),
):
    book = await service.create_book(book_in)
    response.headers["Location"] = f"/books/{book.id}"
    return book


@app.delete("/books/{book_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    service: BookService = Depends(get_service),
):
    # idempotent delete: always return 204
    await service.delete_book(book_id)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
