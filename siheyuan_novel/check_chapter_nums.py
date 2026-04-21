#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查章节编号连续性
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

# 检查章节编号
print("检查章节编号连续性...")
prev_num = 0
missing = []
duplicate = []
seen_nums = set()

for i, chapter in enumerate(unique_chapters, 1):
    num = get_chapter_num(chapter)
    if num == 0:
        print(f"{i:3d}. [无编号] {chapter}")
        continue
    
    if num in seen_nums:
        duplicate.append(f"{num} - {chapter}")
    seen_nums.add(num)
    
    if prev_num != 0 and num != prev_num + 1:
        for missing_num in range(prev_num + 1, num):
            missing.append(missing_num)
    
    prev_num = num

print(f"\n总章节数: {len(unique_chapters)}")
print(f"最高章节号: {prev_num}")

if missing:
    print(f"\n缺失章节号: {len(missing)} 个")
    print(f"前50个缺失: {missing[:50]}")

if duplicate:
    print(f"\n重复章节号: {len(duplicate)} 个")
    for dup in duplicate[:20]:
        print(f"  {dup}")

print(f"\n前30个章节:")
for i, chapter in enumerate(unique_chapters[:30], 1):
    num = get_chapter_num(chapter)
    print(f"{i:3d}. [{num}] {chapter}")
