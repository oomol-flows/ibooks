# 根据 iBook 数据库中 ZANNOTATIONSTYLE 字段与实测得来
# 颜色是用屏幕取色器取的
# @return color, underline
def parse_style(style_id: int) -> tuple[str, bool]:
  if style_id == 0:
    return "#F34734", True
  elif style_id == 1:
    return "#9AC67C", False
  elif style_id == 2:
    return "#95AAB7", False
  elif style_id == 3:
    return "#EBA21D", False
  elif style_id == 4:
    return "#EA9EAB", False
  elif style_id == 5:
    return "#C8ACC7", False
  else:
    return "#EBA21D", False