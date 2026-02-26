from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm import Book
from models import data


class BookRepository(ABC):
    @abstractmethod
    async def list_all() -> List[Dict]:
        pass

    @abstractmethod
    async def add(self, book: Dict) -> Dict:
        pass

    @abstractmethod
    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        pass

    @abstractmethod
    async def delete_by_id(self, book_id: UUID) -> bool:
        pass


class BookRepositoryMemory(BookRepository):
    def __init__(self):
        # Use the shared in-memory list from models.data
        self._books: List[Dict] = data.BOOKS

    async def list_all(self) -> List[Dict]:
        return self._books

    async def add(self, book: Dict) -> Dict:
        self._books.append(book)
        return book

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        sid = str(book_id)
        for b in self._books:
            if b["id"] == sid:
                return b
        return None

    async def delete_by_id(self, book_id: UUID) -> bool:
        sid = str(book_id)
        for i, b in enumerate(self._books):
            if b["id"] == sid:
                self._books.pop(i)
                return True

        return False


class BookRepositoryDB(BookRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> List[Dict]:
        q = select(Book)
        res = await self.session.execute(q)
        rows = res.scalars().all()
        return [r.to_dict() for r in rows]

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        q = select(Book).where(Book.id == str(book_id))
        res = await self.session.execute(q)
        book = res.scalars().first()
        return book.to_dict() if book else None

    async def add(self, book: Dict) -> Dict:
        obj = Book(
            id=book["id"],
            title=book["title"],
            author=book["author"],
            description=book.get("description"),
            status=book.get("status"),
            year=book.get("year"),
        )
        self.session.add(obj)
        await self.session.commit()
        return obj.to_dict()

    async def delete_by_id(self, book_id: UUID) -> bool:
        q = select(Book).where(Book.id == str(book_id))
        res = await self.session.execute(q)
        book = res.scalars().first()
        if not book:
            return False
        await self.session.delete(book)
        await self.session.commit()
        return True
