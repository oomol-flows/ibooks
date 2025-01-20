import re
import os

def find_matched_file(dir_path: str, expression: str):
  pattern = re.compile(expression)
  for file in os.listdir(dir_path):
    if pattern.match(file):
      return os.path.join(dir_path, file)
  raise Exception(f"cannot find file in {dir_path}")

def norm_path(path: str):
  cells = path.split("/iCloud~com~apple~iBooks/Documents/")
  if len(cells) > 1:
    return cells[-1]
  else:
    return path

def with_short(full: str, short: str):
  _full = as_none(full)
  _short = as_none(short)

  if _full is None:
    return _short, None
  else:
    return _full, _short

def as_none(text: str | None):
  if text is None:
    return None
  elif text.strip() == "":
    return None
  else:
    return text