import os
import sqlite3

from oocana import Context

def main(params: dict, context: Context):
  documents_path: str = params["documents"]
  database_path = os.path.join(documents_path, "AEAnnotation", "AEAnnotation_v10312011_1727_local.sqlite")

  # with sqlite3.connect(database_path) as conn:
  #   cursor = conn.cursor()
  #   cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
  #   for row in cursor.fetchall():
  #     print(row)
  #   return

  with sqlite3.connect(database_path) as conn:
    cursor = conn.cursor()
    cursor.execute("select ZANNOTATIONASSETID, ZANNOTATIONREPRESENTATIVETEXT, ZANNOTATIONSELECTEDTEXT, ZANNOTATIONNOTE from `ZAEANNOTATION` where `ZANNOTATIONASSETID` == \"223538F826C31B2307DE69930C1A6037\" order by `ZANNOTATIONASSETID`,`ZPLLOCATIONRANGESTART`")
    column_names = [desc[0] for desc in cursor.description]
    count = 0
    print(">>>")
    for row in cursor.fetchall():
      print(dict(zip(column_names, row)))
      print(str(row[-1]))
      count += 1
      if count > 100:
        break
    print(count)
