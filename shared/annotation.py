import os
import sqlite3
import epubcfi

from . import APPLE_OFFSET
from .utils import find_matched_file, as_none
from .types import Anotation


def search_highlights(id: str, documents_path: str, limit: int | None) -> list[Anotation]:
  sqlite_path = find_matched_file(
    dir_path=os.path.join(documents_path, "AEAnnotation"),
    expression=r"^AEAnnotation[\w\_]+_local.sqlite$",
  )
  highlights = list(_search_highlights(sqlite_path, id, limit))
  highlights.sort(key=lambda x: x[0])

  return [h for _, h in highlights]

def _search_highlights(sqlite_path: str, id: str, limit: int | None):
  with sqlite3.connect(sqlite_path) as conn:
    cursor = conn.cursor()
    sql = """
      SELECT
        ZANNOTATIONASSETID,
        ZANNOTATIONLOCATION,
        ZANNOTATIONNOTE,
        ZANNOTATIONSELECTEDTEXT,
        ZANNOTATIONREPRESENTATIVETEXT,
        ZANNOTATIONSTYLE,
        ZANNOTATIONCREATIONDATE,
        ZANNOTATIONMODIFICATIONDATE
      FROM ZAEANNOTATION
      WHERE ZANNOTATIONASSETID == ?
    """
    if limit is not None:
      sql += " LIMIT ?"
    if limit is None:
      cursor.execute(sql, (id,))
    else:
      cursor.execute(sql, (id, limit))

    for row in cursor.fetchall():
      epubcfi_text: str | None = row[1]
      epubcfi_parsed: epubcfi.ParsedPath | None = None
      if epubcfi_text is not None:
        epubcfi_parsed = epubcfi.parse(epubcfi_text)

      if epubcfi_parsed is not None:
        yield epubcfi_parsed, Anotation(
          id=row[0],
          epubcfi=epubcfi_parsed,
          note=as_none(row[2]),
          selected=row[3],
          representative=row[4],
          style_id=row[5],
          created_at=row[6] + APPLE_OFFSET,
          updated_at=row[7] + APPLE_OFFSET,
        )