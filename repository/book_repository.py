from typing import Dict, List, Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient

from schemas.book import BookStatus


class BookRepository:
    def __init__(self, db: AsyncIOMotorClient):
        self.collection = db.library.books

    async def list_all(
        self,
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
    ) -> List[Dict]:
        query = {}
        if author:
            query["author"] = author
        if status:
            query["status"] = status.value

        cursor = self.collection.find(query)
        if sort_by:
            sort_field = [(sort_by, 1)]
            cursor = cursor.sort(sort_field)

        cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        return [doc async for doc in cursor]

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        return await self.collection.find_one({"id": str(book_id)})

    async def add(self, book: Dict) -> Dict:
        await self.collection.insert_one(book)
        return book

    async def delete_by_id(self, book_id: UUID) -> bool:
        result = await self.collection.delete_one({"id": str(book_id)})
        return result.deleted_count > 0
