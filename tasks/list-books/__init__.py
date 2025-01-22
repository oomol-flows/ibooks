from oocana import Context
from shared.books import search_books

def main(params: dict, context: Context):
  documents_path: str = params["documents"]
  limit: int | None = params["limit"]
  books = list(search_books(documents_path, limit))
  return { "books": books }