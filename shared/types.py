from dataclasses import dataclass
from typing import Literal
from epubcfi import ParsedPath

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

@dataclass
class Annotation:
  id: str
  epubcfi: ParsedPath | None
  note: str | None
  selected: str
  representative: str
  style_id: int
  created_at: float
  updated_at: float
