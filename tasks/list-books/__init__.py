from oocana import Context
from shared.books import search_books

def main(params: dict, context: Context):
  database_path: str = params["database"]
  limit: int | None = params["limit"]
  books = list(search_books(database_path, limit))
  return { "books": books }