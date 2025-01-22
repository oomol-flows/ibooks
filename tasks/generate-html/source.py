from io import StringIO
from html import escape
from shared.types import Anotation

def render_source(buffer: StringIO, annotation: Anotation):
  representative = annotation.representative
  selected = annotation.selected
  offset = representative.find(selected)

  if offset == -1:
    buffer.write(escape(representative)) # 一般不会这样，此乃兜底方案
    return

  before = representative[:offset]
  after = representative[offset + len(selected):]

  if before.strip() != "":
    buffer.write('<span>')
    buffer.write(escape(before))
    buffer.write('</span>\n')

  if selected.strip() != "":
    buffer.write(f'<span class="highlight-style-{annotation.style_id}">')
    buffer.write(escape(selected))
    buffer.write('</span>\n')

  if after.strip() != "":
    buffer.write('<span>')
    buffer.write(escape(after))
    buffer.write('</span>\n')
