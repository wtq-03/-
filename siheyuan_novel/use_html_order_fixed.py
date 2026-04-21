#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用HTML中的正确章节顺序 - 修复版
"""

import os
import re
import shutil
from bs4 import BeautifulSoup

def main():
    # 读取章节列表HTML
    with open('mayiwsk_chapters.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    chapter_list = soup.find('div', id='list')
    
    # 获取所有章节链接和标题（按HTML中的顺序）
    chapters = []
    for a in chapter_list.find_all('a', href=True):
        title = a.get_text(strip=True)
        if title and ('章' in title or '第' in title):
            chapters.append(title)
    
    # 去重，保持顺序
    seen = set()
    ordered_chapters = []
    for title in chapters:
        if title not in seen:
            seen.add(title)
            ordered_chapters.append(title)
    
    # 现在按章节号排序，确保正确的顺序
    def get_chapter_num(title):
        match = re.search(r'第(\d+)章', title)
        return int(match.group(1)) if match else 9999
    
    ordered_chapters.sort(key=get_chapter_num)
    
    print(f"共 {len(ordered_chapters)} 个章节（按章节号排序）")
    
    # 建立标题到文件的映射，并建立可用文件名列表
    available_files = []
    for filename in os.listdir('.'):
        if filename.endswith('.txt'):
            if filename == '坚持原创，杜绝违规承诺书.txt':
                continue
            
            match = re.match(r'[0-9]+_(.*?)\.txt', filename)
            if match:
                title = match.group(1)
                available_files.append((title, filename))
    
    print(f"找到 {len(available_files)} 个章节文件")
    
    # 创建临时目录
    temp_dir = 'temp_html_order'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # 处理章节
    success_count = 0
    missing = []
    used_files = set()
    
    for idx, chapter_title in enumerate(ordered_chapters, 1):
        safe_title = re.sub(r'[\\/:*?"<>|]', '', chapter_title)
        
        # 查找匹配的文件
        found_file = None
        for title, filename in available_files:
            if filename not in used_files:
                if chapter_title in title or title in chapter_title:
                    found_file = filename
                    break
        
        if found_file:
            new_filename = f"{temp_dir}/{idx:04d}_{safe_title}.txt"
            shutil.copy(found_file, new_filename)
            used_files.add(found_file)
            success_count += 1
        else:
            missing.append(chapter_title)
    
    print(f"\n成功处理: {success_count} 个章节")
    
    if missing:
        print(f"缺失章节: {len(missing)} 个")
        for chapter in missing[:10]:
            print(f"  - {chapter}")
    
    # 备份原文件
    backup_dir = 'final_backup'
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    os.makedirs(backup_dir)
    
    for filename in os.listdir('.'):
        if filename.endswith('.txt'):
            shutil.move(filename, f'{backup_dir}/{filename}')
    
    # 移动新文件
    for filename in os.listdir(temp_dir):
        shutil.move(f'{temp_dir}/{filename}', filename)
    
    shutil.rmtree(temp_dir)
    
    print(f"\n完成！现在有 {len([f for f in os.listdir('.') if f.endswith('.txt')])} 个章节文件")
    print(f"备份在 {backup_dir}")
    
    chapter_files = sorted([f for f in os.listdir('.') if f.endswith('.txt')])
    if chapter_files:
        print(f"第一个文件: {chapter_files[0]}")
        print(f"最后一个文件: {chapter_files[-1]}")

if __name__ == '__main__':
    main()
