from typing import Dict

from sqlalchemy import Column, String, Integer, Text, Enum, DateTime, func
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class BookStatusEnum(str, enum.Enum):
    available = "available"
    issued = "issued"


class Book(Base):
    __tablename__ = "books"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(BookStatusEnum), nullable=False, default=BookStatusEnum.available
    )
    year = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "status": self.status,
            "year": self.year,
        }
