from typing import List, Dict, Optional
from uuid import UUID

from models import data


class BookRepository:
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
