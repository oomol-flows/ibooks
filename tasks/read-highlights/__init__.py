import epubcfi

from oocana import Context
from epubcfi.parser import ParsedPath
from shared.annotation import search_highlights


def main(params: dict, context: Context):
  id: str = params["id"]
  documents_path: str = params["documents"]
  limit: int | None = params["limit"]
  highlights = search_highlights(id, documents_path, limit)

  return { "highlights": [
    {
      **highlight.__dict__,
      "epubcfi": _str_epubcfi(highlight.epubcfi),
    }
    for highlight in highlights
  ]}

def _str_epubcfi(cfi: ParsedPath | None):
  if cfi is None:
    return None
  text = epubcfi.format(cfi)
  return f"epubcfi({text})"
