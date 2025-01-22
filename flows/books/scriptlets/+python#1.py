def main(params: dict):
  file_path: str = params["file_path"]
  with open(file_path, "r", encoding="utf8") as f:
    return { "text": f.read() }
