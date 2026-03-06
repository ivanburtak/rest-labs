from typing import Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm import Book
from schemas.book import BookStatus


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(
        self,
        status: Optional[BookStatus] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Tuple[List[Dict], str]:
        if limit == 0:
            print("Passing in limit of 0")
            return ([], None)

        q = select(Book)

        if status:
            q = q.filter_by(status=status)
        if author:
            q = q.filter_by(author=author)

        if sort_by:
            if sort_by == "title":
                sort_col = Book.title
            elif sort_by == "year":
                sort_col = Book.year
            else:
                raise ValueError(f"Invalid sort_by value: {sort_by}")

        if limit:
            q = q.limit(limit)

        if cursor is not None:
            parts = cursor.split(",", 2)
            if len(parts) == 0:
                print("Passing in an empty cursor")
                return ([], None)

            if sort_col is Book.seq:
                q = q.where(Book.seq > int(parts[0]))
            else:
                cursor_time = parts[0]
                cursor_uuid = int(parts[1])

                q = q.where(
                    (Book.created_at > cursor_time)
                    | ((Book.created_at == cursor_time) & (Book.id > cursor_uuid))
                )

        q = q.order_by(sort_col, Book.seq)

        res = await self.session.execute(q)
        rows = res.scalars().all()
        next_cursor: Optional[str] = None
        if len(rows) == limit:
            last = rows[-1]
            next_cursor = (
                f"{last.seq},{last.year}" if sort_col != Book.seq else str(last.seq)
            )
        return ([r.to_dict() for r in rows], next_cursor)

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

        # last_seq = await self.session.scalar(select(func.max(Book.seq)))
        # obj.seq = last_seq + 1 if last_seq is not None else 0

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
