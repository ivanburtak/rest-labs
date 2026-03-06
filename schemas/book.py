from enum import Enum
from typing import Optional, Annotated, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


class BookBase(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    author: Annotated[str, Field(min_length=1)]
    description: Optional[str] = None
    status: BookStatus = Field(default=BookStatus.available)
    year: Annotated[int, Field(ge=0, le=2100)]


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class BookListResponse(BaseModel):
    count: int
    next: Optional[str]
    result: List[BookRead]
