from typing import List, Optional
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
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[BookRead]:
        raw = await self.repo.list_all()
        # filter
        if status is not None:
            raw = [b for b in raw if b.get("status") == status.value]
        if author:
            raw = [
                b
                for b in raw
                if b.get("author") and author.lower() in b.get("author").lower()
            ]

        # sort
        if sort_by:
            key = None
            if sort_by == "title":
                key = lambda x: x.get("title", "")
            elif sort_by == "year":
                key = lambda x: x.get("year", 0)
            if key:
                raw = sorted(raw, key=key)

        # apply pagination
        if limit is not None:
            raw = raw[offset : offset + limit]
        elif offset:
            raw = raw[offset:]

        return [BookRead(**b) for b in raw]

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
