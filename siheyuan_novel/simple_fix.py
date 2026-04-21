#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单修复：删除重复文件，重新编号
"""

import os
import re

def main():
    # 收集所有有效章节文件
    chapter_files = []
    
    for filename in os.listdir('.'):
        if filename.endswith('.txt'):
            if filename == '坚持原创，杜绝违规承诺书.txt':
                continue
            
            # 提取标题部分
            match = re.match(r'[0-9]+_(.*?)\.txt', filename)
            if match:
                title = match.group(1)
                chapter_files.append((title, filename))
    
    print(f"找到 {len(chapter_files)} 个章节文件")
    
    # 去重：保留每个标题的第一个出现
    seen_titles = set()
    unique_files = []
    for title, filename in sorted(chapter_files, key=lambda x: x[0]):
        if title not in seen_titles:
            seen_titles.add(title)
            unique_files.append((title, filename))
    
    print(f"去重后: {len(unique_files)} 个章节")
    
    # 现在按章节号排序
    def get_chapter_num_from_title(title):
        match = re.search(r'第(\d+)章', title)
        return int(match.group(1)) if match else 9999
    
    unique_files.sort(key=lambda x: get_chapter_num_from_title(x[0]))
    
    # 创建临时目录
    temp_dir = 'temp_simple'
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # 重新编号
    for idx, (title, old_filename) in enumerate(unique_files, 1):
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
        new_filename = f"{temp_dir}/{idx:04d}_{safe_title}.txt"
        import shutil
        shutil.copy(old_filename, new_filename)
    
    print(f"重新编号完成，共 {len(unique_files)} 个章节")
    
    # 替换原目录
    print("更新原目录...")
    
    # 备份
    backup_dir = 'backup_before_simple_fix'
    if os.path.exists(backup_dir):
        import shutil
        shutil.rmtree(backup_dir)
    os.makedirs(backup_dir)
    
    for filename in os.listdir('.'):
        if filename.endswith('.txt'):
            import shutil
            shutil.move(filename, f'{backup_dir}/{filename}')
    
    # 移动新文件
    for filename in os.listdir(temp_dir):
        import shutil
        shutil.move(f'{temp_dir}/{filename}', filename)
    
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"\n修复完成！现在有 {len([f for f in os.listdir('.') if f.endswith('.txt')])} 个章节文件")
    print(f"备份在 {backup_dir}")

if __name__ == '__main__':
    main()
