#!/usr/bin/env python3
import os
import re

# 定义小说目录
novel_dir = "/workspace/siheyuan_fanfiction_new"

# 遍历目录，统计每章的字数
def count_chapter_words():
    total_words = 0
    chapter_count = 0
    
    for root, dirs, files in os.walk(novel_dir):
        for file in files:
            if file.endswith(".txt") and "第" in file:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 统计中文字符数
                        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', content)
                        word_count = len(chinese_chars)
                        total_words += word_count
                        chapter_count += 1
                        
                        # 输出每章的字数
                        print(f"{file}: {word_count} 字")
                        
                        # 检查是否在3600-4400字之间
                        if word_count < 3600:
                            print(f"  警告: 字数不足，需要增加 {3600 - word_count} 字")
                        elif word_count > 4400:
                            print(f"  警告: 字数过多，需要减少 {word_count - 4400} 字")
                except Exception as e:
                    print(f"处理文件 {file} 时出错: {e}")
    
    # 输出总字数和平均字数
    if chapter_count > 0:
        avg_words = total_words // chapter_count
        print(f"\n总章节数: {chapter_count}")
        print(f"总字数: {total_words}")
        print(f"平均每章字数: {avg_words}")

if __name__ == "__main__":
    count_chapter_words()