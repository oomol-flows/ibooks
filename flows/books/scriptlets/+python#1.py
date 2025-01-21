from io import StringIO
from html import escape
from epubcfi import split
from epubcfi.parser import ParsedPath
from shared.types import Anotation

def main(params: dict):
  buffer = StringIO()
  buffer.write("<html><body>")
  for highlight in _search_highlights(params["highlights"]):
    if highlight.selected is None and highlight.note is None:
      continue
    buffer.write("<div>")
    if highlight.selected is not None:
      buffer.write("<blockquote>")
      buffer.write(escape(highlight.selected))
      buffer.write("</blockquote>")
    if highlight.note is not None:
      buffer.write("<p>")
      buffer.write(escape(highlight.note))
      buffer.write("</p>")
    buffer.write("</div>")

  buffer.write("</body></html>")
  return { "html": buffer.getvalue() }

def _search_highlights(highlights: list[dict]):
  for highlight in highlights:
    expression: str | None = highlight["epubcfi"]
    path: ParsedPath | None = None
    if expression is not None:
      _, path = split(expression)
    highlight["epubcfi"] = path
    yield Anotation(**highlight)
