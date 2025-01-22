import os
import sqlite3

from typing import Any, Generator
from . import APPLE_OFFSET
from .utils import find_matched_file, norm_path, as_none, with_short
from .types import Book, BookEntity

def search_books(documents_path: str, limit: int | None) -> Generator[Book, None, None]:
  sqlite_path = _sqlite_path(documents_path)
  for book in _list_books(sqlite_path, limit):
    yield book

def get_book(documents_path: str, setid: str) -> Book | None:
  sqlite_path = _sqlite_path(documents_path)
  with sqlite3.connect(sqlite_path) as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
      SELECT
        ZCONTENTTYPE, ZASSETID,
        ZTITLE, ZSORTTITLE,
        ZAUTHOR, ZSORTAUTHOR,
        ZGENRE,
        ZBOOKDESCRIPTION,
        ZPATH, ZASSETDETAILSMODIFICATIONDATE
      FROM ZBKLIBRARYASSET
      WHERE ZASSETID = ?
      """,
      (setid,),
    )
    row = cursor.fetchone()
    if row is None:
      return row
    return _row_to_book(row)

def _sqlite_path(documents_path: str):
  return find_matched_file(
    dir_path=os.path.join(documents_path, "BKLibrary"),
    expression=r"^BKLibrary[\d\-]+\.sqlite$",
  )

def _list_books(sqlite_path: str, limit: int | None):
  with sqlite3.connect(sqlite_path) as conn:
    cursor = conn.cursor()
    sql = """
      SELECT
        ZCONTENTTYPE, ZASSETID,
        ZTITLE, ZSORTTITLE,
        ZAUTHOR, ZSORTAUTHOR,
        ZGENRE,
        ZBOOKDESCRIPTION,
        ZPATH, ZASSETDETAILSMODIFICATIONDATE
      FROM ZBKLIBRARYASSET
      ORDER BY ZASSETDETAILSMODIFICATIONDATE DESC
    """
    if limit is not None:
      sql += " LIMIT ?"
    if limit is None:
      cursor.execute(sql)
    else:
      cursor.execute(sql, (limit,))

    for row in cursor.fetchall():
      book = _row_to_book(row)
      if book is not None:
        yield book

def _row_to_book(row: Any):
    entity = _parse_entity(row[0])
    if entity is None:
      return None
    title, short_title = with_short(row[2], row[3])
    author, short_author = with_short(row[4], row[5])

    return Book(
      id=row[1],
      entity=entity,
      title=title,
      short_title=short_title,
      author=author,
      short_author=short_author,
      genre=as_none(row[6]),
      description=as_none(row[7]),
      path=norm_path(row[8]),
      updated_at=row[9] + APPLE_OFFSET,
    )

def _parse_entity(entity: int) -> BookEntity | None:
  if entity == 1:
    return "epub"
  elif entity == 3:
    return "pdf"
  else:
    return None