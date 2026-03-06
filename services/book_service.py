from typing import List, Optional, Tuple
from uuid import uuid4, UUID
from repository.book_repository import BookRepository
from schemas.book import BookCreate, BookRead, BookStatus


class BookService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    async def get_books(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Tuple[List[BookRead], Optional[str]]:
        raw, next = await self.repo.list_all(
            status=status, author=author, sort_by=sort_by, cursor=cursor, limit=limit
        )

        return ([BookRead(**b) for b in raw], next)

    async def get_book(self, book_id: UUID) -> Optional[BookRead]:
        b = await self.repo.get_by_id(book_id)
        return BookRead(**b) if b else None

    async def create_book(self, book_in: BookCreate) -> BookRead:
        new = book_in.model_dump()
        new_id = str(uuid4())
        new["id"] = new_id
        new["status"] = book_in.status.value
        await self.repo.add(new)
        return BookRead(**new)

    async def delete_book(self, book_id: UUID) -> None:
        # idempotent: remove if present, otherwise do nothing
        await self.repo.delete_by_id(book_id)
