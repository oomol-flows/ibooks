import os

from oocana import Context
from epubcfi import ParsedPath, EpubNode
from shared.books import get_book, Book
from shared.annotation import search_highlights
from shared.types import Annotation


def main(params: dict, context: Context):
  id: str = params["id"]
  database_path: str = params["database"]
  documents_path: str = params["documents"]
  limit: int | None = params["limit"]
  book = get_book(database_path, id)
  if book is None:
    raise ValueError(f"cannot find book (id={id})")
  if book.entity != "epub":
    raise ValueError(f"unsupported book type (entity={book.entity})")

  highlights = search_highlights(id, database_path, limit)
  target: list[dict] = []

  for label, highlights in _group_highlights(book, documents_path, highlights):
    target.append({
      "label": label,
      "highlights": [
        {
          **highlight.__dict__,
          "epubcfi": _str_epubcfi(highlight.epubcfi),
        }
        for highlight in highlights
      ],
    })
  return {
    "book": book,
    "highlights": target,
  }

def _group_highlights(book: Book, documents_path: str, highlights: list[Annotation]):
  with EpubNode() as epub:
    epub_path = os.path.join(documents_path, book.path)
    labels: list[str] = []
    group: dict[str, list[Annotation]] = {}

    for highlight in highlights:
      epubcfi = highlight.epubcfi
      label: str | None = None
      if epubcfi is not None:
        label = epub.ncx_label(epub_path, epubcfi)
      if label is None:
        label = "__no_ncx_label__"
      label_highlights = group.get(label, None)
      if label_highlights is None:
        label_highlights = []
        group[label] = label_highlights
        labels.append(label)
      label_highlights.append(highlight)

    for label in labels:
      yield label, group[label]

def _str_epubcfi(cfi: ParsedPath | None):
  if cfi is None:
    return None
  return f"epubcfi({cfi})"
