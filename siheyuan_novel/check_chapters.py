#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查章节列表
"""

import re
from bs4 import BeautifulSoup

# 读取章节列表HTML
with open('mayiwsk_chapters.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
chapter_list = soup.find('div', id='list')

# 获取所有章节链接和标题
chapters = []
for a in chapter_list.find_all('a', href=True):
    title = a.get_text(strip=True)
    if title and ('章' in title or '第' in title):
        chapters.append(title)

# 去重并按顺序排序
seen = set()
unique_chapters = []
for title in chapters:
    if title not in seen:
        seen.add(title)
        unique_chapters.append(title)

# 尝试按章节号排序
def get_chapter_num(title):
    match = re.search(r'第(\d+)章', title)
    return int(match.group(1)) if match else 0

unique_chapters.sort(key=get_chapter_num)

print(f"从HTML中找到 {len(unique_chapters)} 个章节")
print(f"第一个章节: {unique_chapters[0]}")
print(f"最后一个章节: {unique_chapters[-1]}")
print("\n前20个章节:")
for i, chapter in enumerate(unique_chapters[:20], 1):
    print(f"{i:3d}. {chapter}")
print("\n后20个章节:")
for i, chapter in enumerate(unique_chapters[-20:], len(unique_chapters)-19):
    print(f"{i:3d}. {chapter}")
