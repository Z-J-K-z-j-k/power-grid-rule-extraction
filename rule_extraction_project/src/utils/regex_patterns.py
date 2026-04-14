"""Regex patterns for regulation structure markers."""

import re

# 第X章 / 第X节 / 第X条
RE_CHAPTER = re.compile(r"第[一二三四五六七八九十百千万零〇两]+章")
RE_SECTION = re.compile(r"第[一二三四五六七八九十百千万零〇两]+节")
RE_ARTICLE = re.compile(r"第[一二三四五六七八九十百千万零〇两]+条")

# （一）（二）
RE_CN_ENUM_PAREN = re.compile(r"[（(][一二三四五六七八九十]+[）)]")

# 1. / 1． / 1、
RE_NUM_ITEM = re.compile(r"(?:^|\n)\s*(\d{1,3})[\.．、]\s*")
