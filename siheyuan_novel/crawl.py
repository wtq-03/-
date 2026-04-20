#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取小说《四合院：我不爽，都别想好过》的完整内容
"""

import os
import re
import time
import random
import urllib.request
import urllib.error

# 小说基础信息
NOVEL_NAME = "四合院：我不爽，都别想好过"
BASE_URL = "http://wap.faloo.com"
LIST_URL = "http://wap.faloo.com/booklist/1238319.html"
OUTPUT_DIR = "./"

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': BASE_URL
}

def get_html(url):
    """获取页面HTML内容"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            # 直接读取并返回原始内容
            content = response.read()
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'gb2312']
            for encoding in encodings:
                try:
                    html = content.decode(encoding)
                    return html
                except UnicodeDecodeError:
                    continue
            # 如果都失败，返回原始内容的字符串表示
            return str(content)
    except urllib.error.URLError as e:
        print(f"URL错误 {url}: {e}")
        return None
    except urllib.error.HTTPError as e:
        print(f"HTTP错误 {url}: {e}")
        return None
    except Exception as e:
        print(f"其他错误 {url}: {e}")
        return None

def parse_chapter_list():
    """解析章节列表"""
    html = get_html(LIST_URL)
    if not html:
        return []
    
    # 使用正则表达式提取章节链接
    pattern = r'<a href="(//wap\.faloo\.com/1238319_\d+\.html)".*?>(.*?)</a>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    chapters = []
    for href, title in matches:
        # 清理标题
        title = re.sub(r'<[^>]+>', '', title).strip()
        if title and '章' in title:
            # 构建完整URL
            if href.startswith('//'):
                url = 'http:' + href
            else:
                url = href
            chapters.append({
                'title': title,
                'url': url
            })
    
    # 去重并按章节号排序
    seen = set()
    unique_chapters = []
    for chapter in chapters:
        if chapter['url'] not in seen:
            seen.add(chapter['url'])
            unique_chapters.append(chapter)
    
    # 尝试按章节号排序
    def get_chapter_num(title):
        match = re.search(r'第(\d+)章', title)
        return int(match.group(1)) if match else 0
    
    unique_chapters.sort(key=lambda x: get_chapter_num(x['title']))
    return unique_chapters

def parse_chapter_content(url):
    """解析章节内容"""
    html = get_html(url)
    if not html:
        return None
    
    # 使用正则表达式提取内容
    # 尝试不同的内容模式
    patterns = [
        r'<div class="novel_content">(.*?)</div>',
        r'<div id="content">(.*?)</div>',
        r'<p>(.*?)</p>',
    ]
    
    content = None
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        if matches:
            content = '\n\n'.join(matches)
            break
    
    if content:
        # 清理内容
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', '\n\n', content)
        content = re.sub(r'[\r\n]+', '\n\n', content)
        return content.strip()
    
    return None

def save_chapter(title, content, index):
    """保存章节内容"""
    # 清理文件名
    safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
    filename = f"{OUTPUT_DIR}/{index:04d}_{safe_title}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n\n{content}")
        print(f"保存成功: {filename}")
        return True
    except Exception as e:
        print(f"保存失败 {filename}: {e}")
        return False

def main():
    print(f"开始爬取《{NOVEL_NAME}》...")
    
    # 解析章节列表
    chapters = parse_chapter_list()
    if not chapters:
        print("无法获取章节列表")
        return
    
    print(f"找到 {len(chapters)} 个章节")
    
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 爬取所有章节
    success_count = 0
    failure_count = 0
    
    for i, chapter in enumerate(chapters, 1):
        print(f"\n爬取第 {i}/{len(chapters)} 章: {chapter['title']}")
        print(f"URL: {chapter['url']}")
        
        content = parse_chapter_content(chapter['url'])
        if content:
            if save_chapter(chapter['title'], content, i):
                success_count += 1
            else:
                failure_count += 1
        else:
            print(f"无法获取章节内容: {chapter['title']}")
            failure_count += 1
        
        # 随机延迟，避免被反爬
        delay = random.uniform(1, 3)
        print(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
    
    print(f"\n爬取完成！")
    print(f"成功: {success_count} 个章节")
    print(f"失败: {failure_count} 个章节")

if __name__ == "__main__":
    main()
