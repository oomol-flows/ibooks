from dataclasses import dataclass
from typing import Literal

BookEntity = Literal["epub", "pdf"]

@dataclass
class Book:
  id: str
  entity: BookEntity
  title: str | None
  short_title: str | None
  author: str | None
  short_author: str | None
  genre: str | None
  description: str | None
  path: str
  updated_at: float
