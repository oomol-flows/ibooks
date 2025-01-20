import re
import os

def find_matched_file(dir_path: str, expression: str):
  pattern = re.compile(expression)
  for file in os.listdir(dir_path):
    if pattern.match(file):
      return os.path.join(dir_path, file)
  raise Exception(f"cannot find file in {dir_path}")