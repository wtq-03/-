#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复章节文件编号问题
"""

import os
import re
from bs4 import BeautifulSoup

def main():
    # 读取章节列表HTML
    with open('mayiwsk_chapters.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    chapter_list = soup.find('div', id='list')
    
    if not chapter_list:
        print("无法找到章节列表")
        return
    
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
    
    print(f"找到 {len(unique_chapters)} 个有效章节")
    
    # 创建临时目录
    temp_dir = 'temp_chapters'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # 收集所有现有文件
    existing_files = {}
    for filename in os.listdir('.'):
        if filename.endswith('.txt') and filename != '坚持原创，杜绝违规承诺书.txt':
            # 从文件名中提取标题
            match = re.match(r'[0-9]+_(.*?)\.txt', filename)
            if match:
                title = match.group(1)
                existing_files[title] = filename
    
    print(f"找到 {len(existing_files)} 个现有章节文件")
    
    # 重新编号并移动到临时目录
    success_count = 0
    missing_chapters = []
    
    for i, chapter_title in enumerate(unique_chapters, 1):
        # 生成安全的文件名
        safe_title = re.sub(r'[\\/:*?"<>|]', '', chapter_title)
        
        # 在现有文件中查找
        found = False
        for title, filename in existing_files.items():
            if chapter_title in title or title in chapter_title:
                # 匹配到了
                new_filename = f"{temp_dir}/{i:04d}_{safe_title}.txt"
                os.rename(filename, new_filename)
                print(f"重命名: {filename} -> {new_filename}")
                success_count += 1
                found = True
                break
        
        if not found:
            missing_chapters.append(chapter_title)
    
    print(f"\n成功处理: {success_count} 个章节")
    if missing_chapters:
        print(f"缺失章节: {len(missing_chapters)} 个")
        for chapter in missing_chapters:
            print(f"  - {chapter}")
    
    # 移动临时目录内容
    print(f"\n清理原目录并移动新文件...")
    for filename in os.listdir('.'):
        if filename.endswith('.txt'):
            os.remove(filename)
    
    for filename in os.listdir(temp_dir):
        os.rename(f"{temp_dir}/{filename}", filename)
    
    os.rmdir(temp_dir)
    
    print("修复完成！")

if __name__ == '__main__':
    main()
