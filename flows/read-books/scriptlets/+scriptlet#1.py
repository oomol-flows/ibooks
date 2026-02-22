from oocana import Context

#region generated meta
import typing
class Inputs(typing.TypedDict):
  books: list[dict]
Outputs = dict[str, typing.Any]
#endregion

async def main(params: Inputs, context: Context) -> Outputs | None:
  books = params["books"]

  # Prepare table data
  headers = ["Title", "ID", "Type"]
  rows = []

  for book in books:
    title = book.get("title", book.get("short_title", "Untitled"))
    book_id = book.get("id", "")
    entity_type = book.get("entity", "").upper()

    rows.append([title, book_id, entity_type])

  # Display as HTML table
  html = """
  <style>
    table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; table-layout: fixed; }
    th { background-color: #4CAF50; color: white; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; }
    .type-cell { width: 80px; }
    .id-cell {
      width: 80px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: pointer;
      color: #0066cc;
      text-decoration: underline;
    }
    .id-cell:hover { color: #004499; }
    .title-cell { word-wrap: break-word; }
  </style>
  <script>
    function copyID(id) {
      navigator.clipboard.writeText(id).then(() => {
        console.log('ID copied: ' + id);
      });
    }
  </script>
  <table>
    <tr><th>Title</th><th class="type-cell">Type</th><th class="id-cell">ID</th></tr>
  """

  for row in rows:
    title = row[0]
    book_id = row[1]
    entity_type = row[2]
    html += f'<tr><td class="title-cell">{title}</td><td class="type-cell">{entity_type}</td><td class="id-cell" onclick="copyID(\'{book_id}\')" title="{book_id}">{book_id}</td></tr>'

  html += "</table>"

  context.preview({
    "type": "html",
    "data": html
  })

  return {}
