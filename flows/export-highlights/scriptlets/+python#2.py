from uuid import uuid4
from shared.types import Book

def main(params: dict):
  book = Book(**params["book"])
  title = book.title or book.short_author
  if title is None:
    title = str(uuid4())

  file_name = title.replace("/", "-")
  file_name = file_name + ".html"

  return { "file_name": file_name }
