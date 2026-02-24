from fastapi import FastAPI, HTTPException, Response, status
from typing import List, Optional
from uuid import UUID

from schemas.book import BookCreate, BookRead, BookStatus
from services.book_service import BookService

app = FastAPI(title="Library API")
service = BookService()


@app.get("/books", response_model=List[BookRead])
async def list_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
):
    """Get all books with optional filtering by status and author, and sorting by title or year."""
    books = await service.get_books(status=status, author=author, sort_by=sort_by)
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
