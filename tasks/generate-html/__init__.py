from io import StringIO
from html import escape
from epubcfi import parse
from epubcfi.parser import ParsedPath
from shared.types import Book, Anotation

def main(params: dict):
  styles: str | None = params["styles"]
  book: Book = Book(**params["book"])

  buffer = StringIO()
  buffer.write("<html>\n")

  _wrtie_head(buffer, book, styles)
  _write_body(buffer, book, params["highlights"])

  buffer.write("</html>")
  return { "html": buffer.getvalue() }

def _wrtie_head(buffer: StringIO, book: Book, styles: str | None):
  title: str | None = book.title or book.short_title
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

def _write_body(buffer: StringIO, book: Book, highlights: list[dict]):
  title: str | None = book.title or book.short_title
  author: str | None = book.author or book.short_author
  a_icon = "https://api.iconify.design/academicons:academia-square.svg?color=%23888888"
  chat_icon = "https://api.iconify.design/fluent-mdl2:message.svg?color=%23888888"

  buffer.write('<body><div class="content">\n')

  if title is not None:
    buffer.write("<h1>")
    buffer.write(escape(title))
    buffer.write("</h1>\n")
  if author is not None:
    buffer.write('<p class="author">')
    buffer.write(escape(author))
    buffer.write("</p>\n")

  if book.description is not None:
    buffer.write('<p class="text">')
    buffer.write(escape(book.description))
    buffer.write("</p>\n")

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
      buffer.write(f'<p class="text highlight-style-{highlight.style_id}">')
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
      path = parse(expression)
    highlight["epubcfi"] = path
    yield Anotation(**highlight)
