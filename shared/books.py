import os
import sqlite3

from typing import Any, Generator
from . import APPLE_OFFSET
from .utils import find_matched_file, norm_path, as_none, with_short
from .types import Book, BookEntity

# Database format from Apple iBook
# {
#     "Z_PK": 1,
#     "Z_ENT": 5,
#     "Z_OPT": 20,
#     "ZCANREDOWNLOAD": 1,
#     "ZCOMBINEDSTATE": 1,
#     "ZCOMPUTEDRATING": None,
#     "ZCONTENTTYPE": 3,
#     "ZDESKTOPSUPPORTLEVEL": 0,
#     "ZDIDRUNFORYOUENDOFBOOKEXPERIENCE": None,
#     "ZDIDWARNABOUTDESKTOPSUPPORT": 0,
#     "ZFILESIZE": 18292316,
#     "ZGENERATION": 1,
#     "ZHASRACSUPPORT": 0,
#     "ZISDEVELOPMENT": 0,
#     "ZISDOWNLOADINGSUPPLEMENTALCONTENT": None,
#     "ZISEPHEMERAL": 0,
#     "ZISEXPLICIT": None,
#     "ZISFINISHED": None,
#     "ZISHIDDEN": 0,
#     "ZISLOCKED": 0,
#     "ZISNEW": 0,
#     "ZISPROOF": 0,
#     "ZISSAMPLE": 0,
#     "ZISSTOREAUDIOBOOK": None,
#     "ZISSUPPLEMENTALCONTENT": 0,
#     "ZISTRACKEDASRECENT": 0,
#     "ZMETADATAMIGRATIONVERSION": None,
#     "ZNOTFINISHED": None,
#     "ZPAGECOUNT": 0,
#     "ZRATING": 0,
#     "ZSERIESISCLOUDONLY": None,
#     "ZSERIESISHIDDEN": None,
#     "ZSERIESNEXTFLAG": None,
#     "ZSERIESSORTKEY": 0,
#     "ZSORTKEY": None,
#     "ZSTATE": 1,
#     "ZTASTE": 0,
#     "ZTASTESYNCEDTOSTORE": 0,
#     "ZLOCALONLYSERIESITEMSPARENT": None,
#     "ZPURCHASEDANDLOCALPARENT": None,
#     "ZSERIESCONTAINER": None,
#     "ZSUPPLEMENTALCONTENTPARENT": None,
#     "ZASSETDETAILSMODIFICATIONDATE": 724808199.958,
#     "ZBOOKHIGHWATERMARKPROGRESS": 0.8873484134674072,
#     "ZBOOKMARKSSERVERMAXMODIFICATIONDATE": None,
#     "ZCREATIONDATE": 694315557.842771,
#     "ZDATEFINISHED": 688104103.911243,
#     "ZDURATION": 0.0,
#     "ZEXPECTEDDATE": None,
#     "ZFILEONDISKLASTTOUCHDATE": None,
#     "ZLASTENGAGEDDATE": 708657280.058927,
#     "ZLASTOPENDATE": 724808194.258559,
#     "ZLOCATIONSERVERMAXMODIFICATIONDATE": None,
#     "ZMODIFICATIONDATE": 712653051.269783,
#     "ZPURCHASEDATE": 694315557.837321,
#     "ZREADINGPROGRESS": 0.7654535174369812,
#     "ZRELEASEDATE": None,
#     "ZUPDATEDATE": 688104054,
#     "ZVERSIONNUMBER": 0.0,
#     "ZACCOUNTID": None,
#     "ZASSETGUID": "23BD73CD-B4BF-4A54-BE7F-DF411E461724",
#     "ZASSETID": "59BFDFF8FB6DC6C81A58DC679779C742",
#     "ZAUTHOR": "Watch Tower Bible and Tract Society of Pennsylvania",
#     "ZBOOKDESCRIPTION": None,
#     "ZBOOKMARKSSERVERVERSION": None,
#     "ZCOMMENTS": None,
#     "ZCOVERURL": None,
#     "ZCOVERWRITINGMODE": None,
#     "ZDATASOURCEIDENTIFIER": "com.apple.ibooks.datasource.ubiquity",
#     "ZDOWNLOADEDDSID": None,
#     "ZEPUBID": "",
#     "ZFAMILYID": None,
#     "ZGENRE": None,
#     "ZGROUPING": None,
#     "ZKIND": None,
#     "ZLANGUAGE": None,
#     "ZLOCATIONSERVERVERSION": None,
#     "ZPAGEPROGRESSIONDIRECTION": None,
#     "ZPATH": "path/to/file.pdf",
#     "ZPERMLINK": None,
#     "ZPURCHASEDDSID": None,
#     "ZSEQUENCEDISPLAYNAME": None,
#     "ZSERIESID": None,
#     "ZSERIESSTACKIDS": None,
#     "ZSORTAUTHOR": "Watch Tower Bible and Tract Society of Pennsylvania",
#     "ZSORTTITLE": "Book tilte",
#     "ZSTOREID": None,
#     "ZSTOREPLAYLISTID": None,
#     "ZTEMPORARYASSETID": None,
#     "ZTITLE": "Book title",
#     "ZVERSIONNUMBERHUMANREADABLE": None,
#     "ZYEAR": None,
#     "ZMAPPEDASSETCONTENTTYPE": 0,
#     "ZSERIESFILTERMODE": None,
#     "ZSERIESISORDERED": None,
#     "ZMAPPEDASSETID": None,
#     "ZGENRES": None,
#     "ZURL": None,
#     "ZAUTHORNAMES": None,
#     "ZCOVERASPECTRATIO": None,
#     "ZNARRATORCOUNT": None,
#     "ZAUTHORCOUNT": None,
#     "ZNARRATORNAMES": None,
#     "ZHASTOOMANYNARRATORS": None,
#     "ZSEQUENCENUMBER": None,
#     "ZSERIESSORTMODE": None,
#     "ZHASTOOMANYAUTHORS": None,
#     "ZFINISHEDDATEKIND": 0
# }

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