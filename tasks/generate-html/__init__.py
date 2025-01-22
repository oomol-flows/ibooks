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
  _write_body(buffer, title, params["highlights"])

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

def _write_body(buffer: StringIO, title: str | None, highlights: list[dict]):
  a_icon = "https://api.iconify.design/academicons:academia-square.svg?color=%23888888"
  chat_icon = "https://api.iconify.design/fluent-mdl2:message.svg?color=%23888888"
  buffer.write('<body><div class="content">\n')

  if title is not None:
    buffer.write("<h1>")
    buffer.write(escape(title))
    buffer.write("</h1>\n")

  for highlight in _search_highlights(highlights):
    if highlight.selected is None and highlight.note is None:
      continue
    if highlight.selected is not None:
      buffer.write('<div class="row source">')
      buffer.write(f'<img class="icon" src="{a_icon}"/>')
      buffer.write('<p class="text">')
      buffer.write(escape(highlight.selected))
      buffer.write("</p></div>\n")

    if highlight.note is not None:
      buffer.write('<div class="row note">')
      buffer.write(f'<img class="icon" src="{chat_icon}"/>')
      buffer.write('<p class="text">')
      buffer.write(escape(highlight.note))
      buffer.write("</p></div>\n")

    buffer.write('<div class="row by-date">')
    buffer.write('<p class="text page">6</p>\n')
    buffer.write('<p class="text dateAndAuthor">12月 19, 17:24, Tom</p>')
    buffer.write("</div>\n")

  buffer.write("</div></body>\n")

def _search_highlights(highlights: list[dict]):
  for highlight in highlights:
    expression: str | None = highlight["epubcfi"]
    path: ParsedPath | None = None
    if expression is not None:
      _, path = split(expression)
    highlight["epubcfi"] = path
    yield Anotation(**highlight)
