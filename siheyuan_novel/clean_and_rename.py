#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理并重新命名章节文件
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
    
    # 现在按章节号排序
    def get_chapter_num(title):
        match = re.search(r'第(\d+)章', title)
        return int(match.group(1)) if match else 9999
    
    ordered_chapters.sort(key=get_chapter_num)
    
    print(f"共 {len(ordered_chapters)} 个章节")
    
    # 创建临时目录
    temp_dir = 'temp_clean'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # 收集现有文件
    existing_files = {}
    for filename in os.listdir('.'):
        if filename.endswith('.txt') and filename != '坚持原创，杜绝违规承诺书.txt':
            existing_files[filename] = filename
    
    print(f"找到 {len(existing_files)} 个现有文件")
    
    # 处理章节
    success_count = 0
    missing = []
    
    for idx, chapter_title in enumerate(ordered_chapters, 1):
        # 生成安全标题
        safe_title = re.sub(r'[\\/:*?"<>|]', '', chapter_title)
        
        # 在现有文件中查找
        found = False
        for filename in list(existing_files.keys()):
            # 从文件名中提取标题部分
            title_part = re.sub(r'^[0-9]+_', '', filename)
            title_part = title_part.replace('.txt', '')
            
            if chapter_title in title_part or title_part in chapter_title:
                # 找到匹配
                new_filename = f"{temp_dir}/{idx:04d}_{safe_title}.txt"
                shutil.copy(filename, new_filename)
                del existing_files[filename]
                success_count += 1
                found = True
                break
        
        if not found:
            missing.append(chapter_title)
    
    print(f"\n成功处理: {success_count} 个章节")
    
    if missing:
        print(f"缺失章节: {len(missing)} 个")
        for chapter in missing[:20]:
            print(f"  - {chapter}")
    
    # 替换原目录
    print("\n更新章节目录...")
    
    # 备份原目录
    if os.path.exists('chapters_backup'):
        shutil.rmtree('chapters_backup')
    os.makedirs('chapters_backup')
    
    for filename in os.listdir('.'):
        if filename.endswith('.txt'):
            shutil.move(filename, f'chapters_backup/{filename}')
    
    # 移动新文件
    for filename in os.listdir(temp_dir):
        shutil.move(f'{temp_dir}/{filename}', filename)
    
    shutil.rmtree(temp_dir)
    
    print(f"\n完成！共 {len(os.listdir('.')) - 1} 个章节文件")
    print(f"备份文件在 chapters_backup 目录")

if __name__ == '__main__':
    main()
