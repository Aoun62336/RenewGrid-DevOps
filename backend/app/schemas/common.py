"""
schemas/common.py — Shared pagination and response wrappers.
"""
from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]


class MessageResponse(BaseModel):
    message: str
