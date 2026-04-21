#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用保存的HTML爬取所有章节
"""

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

NOVEL_NAME = "四合院：我不爽，都别想好过"
OUTPUT_DIR = "./"

session = requests.Session()
session.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
})

def random_delay():
    delay = random.uniform(1, 3)
    time.sleep(delay)

def get_html(url):
    try:
        response = session.get(url, timeout=30, verify=False)
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"获取 {url} 失败: {e}")
        return None

def get_chapter_content(html):
    """提取章节内容"""
    soup = BeautifulSoup(html, 'html.parser')
    
    content_div = soup.find('div', id='content')
    if not content_div:
        content_div = soup.find('div', class_='content')
    if not content_div:
        content_div = soup.find('div', class_='read-content')
    
    if content_div:
        content = content_div.get_text(separator='\n\n', strip=True)
        content = re.sub(r'\s+', '\n\n', content)
        return content
    return None

def main():
    print("加载章节列表...")
    
    # 读取已保存的章节列表
    with open('mayiwsk_chapters.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    chapter_list = soup.find('div', id='list')
    
    chapters = []
    for a in chapter_list.find_all('a', href=True):
        title = a.get_text(strip=True)
        href = a['href']
        if title and ('章' in title or '第' in title):
            if href.startswith('/'):
                url = f"https://www.mayiwsk.com{href}"
            else:
                url = href
            chapters.append({'title': title, 'url': url})
    
    # 去重并排序
    seen = set()
    unique_chapters = []
    for chap in chapters:
        if chap['title'] not in seen:
            seen.add(chap['title'])
            unique_chapters.append(chap)
    
    def get_chapter_num(title):
        match = re.search(r'第(\d+)章', title)
        return int(match.group(1)) if match else 9999
    unique_chapters.sort(key=lambda x: get_chapter_num(x['title']))
    
    print(f"共 {len(unique_chapters)} 个章节")
    
    # 获取已有的文件
    existing = set()
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith('.txt'):
            existing.add(filename)
    
    # 爬取
    success = 0
    for idx, chapter in enumerate(unique_chapters, 1):
        safe_title = re.sub(r'[\\/:*?"<>|]', '', chapter['title'])
        filename = f"{idx:04d}_{safe_title}.txt"
        
        if filename in existing:
            print(f"跳过已存在: {filename}")
            continue
        
        print(f"下载 {idx}/{len(unique_chapters)}: {chapter['title']}")
        
        html = get_html(chapter['url'])
        if not html:
            print(f"获取失败，跳过")
            continue
        
        content = get_chapter_content(html)
        if not content:
            print(f"无法提取内容，跳过")
            continue
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{chapter['title']}\n\n{content}")
        
        print(f"保存成功: {filename}")
        success += 1
        
        random_delay()
    
    print(f"\n完成！共保存 {success} 个新章节")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
