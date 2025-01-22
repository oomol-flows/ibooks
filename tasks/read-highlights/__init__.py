import epubcfi

from oocana import Context
from epubcfi.parser import ParsedPath
from shared.books import get_book
from shared.annotation import search_highlights


def main(params: dict, context: Context):
  id: str = params["id"]
  documents_path: str = params["documents"]
  limit: int | None = params["limit"]
  book = get_book(documents_path, id)
  if book is None:
    raise ValueError(f"cannot find book (id={id})")

  highlights = search_highlights(id, documents_path, limit)
  highlights = [
    {
      **highlight.__dict__,
      "epubcfi": _str_epubcfi(highlight.epubcfi),
    }
    for highlight in highlights
  ]
  return {
    "book": book,
    "highlights": highlights,
  }

def _str_epubcfi(cfi: ParsedPath | None):
  if cfi is None:
    return None
  return f"epubcfi({cfi})"
