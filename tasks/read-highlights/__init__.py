import os
import re
import sqlite3

from oocana import Context
from shared import APPLE_OFFSET
from shared.utils import find_matched_file, as_none
from shared.types import Anotation

def main(params: dict, context: Context):
  id: str = params["id"]
  documents_path: str = params["documents"]
  limit: int | None = params["limit"]
  sqlite_path = find_matched_file(
    dir_path=os.path.join(documents_path, "AEAnnotation"),
    expression=r"^AEAnnotation[\w\_]+_local.sqlite$",
  )
  highlights = list(_list_highlights(sqlite_path, id, limit))
  for l in highlights:
    print(l)


def _list_highlights(sqlite_path: str, id: str, limit: int | None):
  with sqlite3.connect(sqlite_path) as conn:
    cursor = conn.cursor()
    sql = """
      SELECT
        ZANNOTATIONASSETID,
        ZANNOTATIONLOCATION,
        ZANNOTATIONNOTE,
        ZANNOTATIONSELECTEDTEXT,
        ZANNOTATIONREPRESENTATIVETEXT,
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
      yield Anotation(
        id=row[0],
        epubcfi=_parse_epubcfi(row[1]),
        note=as_none(row[2]),
        selected=row[3],
        representative=row[4],
        created_at=row[5] + APPLE_OFFSET,
        updated_at=row[6] + APPLE_OFFSET,
      )

def _parse_epubcfi(epubcfi: str):
  match = re.search(r"epubcfi\((.*?)\)", epubcfi)
  if match is None:
    return epubcfi
  return match.group(1)
