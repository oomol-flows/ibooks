from io import StringIO
from html import escape
from markdown import markdown
from datetime import datetime
from epubcfi import parse, ParsedPath
from shared.types import Book, Annotation
from .source import render_source

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

  buffer.write('<body><div class="root"><div class="content">\n')

  if title is not None:
    buffer.write("<h1>")
    buffer.write(escape(title))
    buffer.write("</h1>\n")
  if author is not None:
    buffer.write('<p class="author">')
    buffer.write(escape(author))
    buffer.write("</p>\n")

  if book.description is not None:
    buffer.write('<p>')
    buffer.write(escape(book.description))
    buffer.write("</p>\n")

  ever_display_label: bool = False

  for label, annotations in _group_annotations(highlights):
    injected_title: str | None = None
    if label is not None:
      ever_display_label = True
      injected_title = label
    elif ever_display_label:
      injected_title = "Others"
    
    if injected_title is not None:
        buffer.write("<h2>")
        buffer.write(escape(injected_title))
        buffer.write("</h2>\n")

    for annotation in annotations:
      if annotation.selected is None and annotation.note is None:
        continue

      cfi_url = _cfi_url(book, annotation)
      buffer.write('<div class="row source">')

      if cfi_url is not None:
        buffer.write(f'<a href="{cfi_url}">')
      buffer.write(f'<img class="icon" src="{a_icon}"/>')
      if cfi_url is not None:
        buffer.write("</a>")

      buffer.write("<p>")
      render_source(buffer, annotation)
      buffer.write("</p></div>\n")

      if annotation.note is not None:
        buffer.write('<div class="row">')
        buffer.write(f'<img class="icon" src="{chat_icon}"/>')
        buffer.write(f'<div class="note note-style-{annotation.style_id}">')
        buffer.write(markdown(annotation.note))
        buffer.write("</div></div>\n")

      buffer.write('<div class="by-date">')
      if abs(annotation.created_at - annotation.updated_at) < 5.0:
        buffer.write(f'<p class="dateAndAuthor">Created at {_format(annotation.created_at)}</p>')
      else:
        buffer.write(f'<p class="dateAndAuthor">Updated at {_format(annotation.updated_at)}</p>')
      buffer.write("</div>\n")

  buffer.write("</div></div></body>\n")

def _group_annotations(highlights: list[dict]):
  no_ncx_highlights: list[dict] = []
  labels_count: int = 0

  for node in highlights:
    if node["label"] == "__no_ncx_label__":
      no_ncx_highlights = node["highlights"]
    else:
      labels_count += 1

  if labels_count != 0:
    for node in highlights:
      label: str = node["label"]
      label_highlights: list[dict] = node["highlights"]
      yield label, list(_search_annotations(label_highlights))
    if len(no_ncx_highlights) > 0:
      yield None, list(_search_annotations(no_ncx_highlights))
  elif len(no_ncx_highlights) > 0:
    yield None, list(_search_annotations(no_ncx_highlights))

def _search_annotations(highlights: list[dict]):
  for highlight in highlights:
    expression: str | None = highlight["epubcfi"]
    path: ParsedPath | None = None
    if expression is not None:
      path = parse(expression)
    params = highlight.copy()
    params["epubcfi"] = path
    yield Annotation(**params)

def _format(timestamp: float) -> str:
  date = datetime.fromtimestamp(timestamp)
  format = date.strftime('%Y-%m-%d %H:%M:%S')
  return format

def _cfi_url(book: Book, annotation: Annotation):
  epubcfi = annotation.epubcfi
  if epubcfi is None:
    return None
  return f"ibooks://assetid/{book.id}#epubcfi({epubcfi})"