import os
import sqlite3
import epubcfi
import functools

from typing import Any
from oocana import Context
from epubcfi.parser import ParsedPath
from . import APPLE_OFFSET
from .utils import find_matched_file, as_none
from .types import Anotation


def search_highlights(id: str, documents_path: str, limit: int | None) -> list[Anotation]:
  sqlite_path = find_matched_file(
    dir_path=os.path.join(documents_path, "AEAnnotation"),
    expression=r"^AEAnnotation[\w\_]+_local.sqlite$",
  )
  highlights = list(_search_highlights(sqlite_path, id, limit))
  highlights.sort(key=functools.cmp_to_key(_compare_nums))
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

      yield _to_nums(epubcfi_parsed), Anotation(
        id=row[0],
        epubcfi=epubcfi_parsed,
        note=as_none(row[2]),
        selected=row[3],
        representative=row[4],
        created_at=row[5] + APPLE_OFFSET,
        updated_at=row[6] + APPLE_OFFSET,
      )

def _str_epubcfi(cfi: ParsedPath | None):
  if cfi is None:
    return None
  return f"epubcfi({cfi})"

def _to_nums(path: epubcfi.ParsedPath | None):
  if path is None:
    return []

  if isinstance(path, epubcfi.PathRange):
    start, _ = epubcfi.to_absolute(path)
    path = start
  
  nums: list[int] = []
  ignore_offset = False

  for step in path.steps:
    if isinstance(step, epubcfi.Step):
      nums.append(step.index)
    else:
      ignore_offset = True
      break

  offset = path.offset

  if not ignore_offset and isinstance(offset, epubcfi.CharacterOffset):
    nums.append(offset.value)
  
  return nums

def _compare_nums(element1: tuple[list[int], Any], element2: tuple[list[int], Any]):
  nums1, _ = element1
  nums2, _ = element2
  length = min(len(nums1), len(nums2))
  for i in range(length):
    num1 = nums1[i]
    num2 = nums2[i]
    if num1 != num2:
      return num1 - num2
  return len(nums1) - len(nums2)
