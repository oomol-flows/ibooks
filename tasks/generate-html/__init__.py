from io import StringIO
from html import escape
from epubcfi import split
from epubcfi.parser import ParsedPath
from shared.types import Anotation

def main(params: dict):
  title: str | None = params["title"]
  styles: str | None = params["styles"]
  buffer = StringIO()
  buffer.write("<html>\n")

  _wrtie_head(buffer, title, styles)
  _write_body(buffer, params["highlights"])

  buffer.write("</html>")
  return { "html": buffer.getvalue() }

def _wrtie_head(buffer: StringIO, title: str | None, styles: str | None):
  buffer.write("<head>\n")
  buffer.write('<meta content="text/html; charset=UTF-8" http-equiv="Content-Type">\n')
  buffer.write('<meta charset="UTF-8">\n')
  buffer.write('<meta content="width=device-width" name="viewport">\n')
  if title is not None:
    buffer.write("<title>")
    buffer.write(escape(title))
    buffer.write("</title>\n")
  if styles is not None:
    buffer.write("<style>")
    buffer.write(styles)
    buffer.write("</style>")
  buffer.write("</head>\n")

def _write_body(buffer: StringIO, highlights: list[dict]):
  buffer.write("<body>")
  for highlight in _search_highlights(highlights):
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
  buffer.write("</body>\n")

def _search_highlights(highlights: list[dict]):
  for highlight in highlights:
    expression: str | None = highlight["epubcfi"]
    path: ParsedPath | None = None
    if expression is not None:
      _, path = split(expression)
    highlight["epubcfi"] = path
    yield Anotation(**highlight)
