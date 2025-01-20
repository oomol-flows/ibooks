import os
import sqlite3

from oocana import Context
from shared import APPLE_OFFSET
from shared.utils import find_matched_file, norm_path, as_none, with_short
from shared.types import Book, BookEntity

def main(params: dict, context: Context):
  documents_path: str = params["documents"]
  limit: int | None = params["limit"]
  sqlite_path = find_matched_file(
    dir_path=os.path.join(documents_path, "BKLibrary"),
    expression=r"^BKLibrary[\d\-]+\.sqlite$",
  )
  books = list(_list_books(sqlite_path, limit))
  return { "books": books }


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
      entity = _parse_entity(row[0])
      if entity is None:
        continue
      title, short_title = with_short(row[2], row[3])
      author, short_author = with_short(row[4], row[5])
      yield Book(
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