#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 mayiwsk.com 网站爬取小说内容
"""

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

# 小说基础信息
NOVEL_NAME = "四合院：我不爽，都别想好过"
NOVEL_URL = "https://www.mayiwsk.com/123_123601/"
OUTPUT_DIR = "./"

# 创建session
session = requests.Session()
session.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
})

# 随机延迟函数
def random_delay(min_delay=2, max_delay=5):
    delay = random.uniform(min_delay, max_delay)
    print(f"等待 {delay:.2f} 秒...")
    time.sleep(delay)

def get_existing_chapters():
    """获取已存在的章节编号"""
    existing = set()
    if os.path.exists(OUTPUT_DIR):
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith('.txt'):
                match = re.match(r'(\d{4})_.*\.txt', filename)
                if match:
                    existing.add(int(match.group(1)))
    return existing

def get_html(url, retry=3):
    """获取页面HTML内容"""
    for attempt in range(retry):
        try:
            response = session.get(url, timeout=20, verify=False)
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as e:
            if attempt < retry - 1:
                print(f"请求错误: {e}，重试中...")
                random_delay(5, 10)
                continue
            return None
    return None

def get_chapter_list():
    """获取章节列表"""
    print("获取章节列表...")
    html = get_html(NOVEL_URL)
    
    if not html:
        print("无法获取章节列表")
        return []
    
    # 保存章节列表页面
    with open('mayiwsk_chapters.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("章节列表已保存到 mayiwsk_chapters.html")
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试找到章节链接
    chapters = []
    
    # 查找章节列表
    chapter_list = soup.find('div', id='list')
    if chapter_list:
        # 找到所有章节链接
        for a in chapter_list.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if title and ('章' in title or '第' in title):
                # 构建完整URL
                if href.startswith('/'):
                    full_url = f"https://www.mayiwsk.com{href}"
                else:
                    full_url = href
                chapters.append({
                    'title': title,
                    'url': full_url
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
    print(f"找到 {len(unique_chapters)} 个章节")
    return unique_chapters

def download_chapter(chapter, chapter_index):
    """下载单个章节"""
    chapter_url = chapter['url']
    chapter_title = chapter['title']
    
    print(f"\n下载章节 {chapter_index}: {chapter_title}")
    print(f"URL: {chapter_url}")
    
    # 尝试访问章节页面
    html = get_html(chapter_url)
    if not html:
        print("无法获取章节内容")
        return False
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试找到内容容器
    content = None
    
    # 查找内容容器
    content_containers = [
        soup.find('div', id='content'),
        soup.find('div', class_='content'),
        soup.find('div', class_='novel_content'),
        soup.find('div', class_='article'),
        soup.find('div', class_='read-content')
    ]
    
    for container in content_containers:
        if container:
            content = container.get_text(separator='\n\n', strip=True)
            break
    
    if not content:
        print("无法获取章节内容")
        return False
    
    # 清理内容
    content = re.sub(r'\s+', '\n\n', content)
    content = re.sub(r'[\r\n]+', '\n\n', content)
    # 移除广告内容
    content = re.sub(r'请记住本书首发域名.*?(?=\n)', '', content)
    content = re.sub(r'手机版阅读网址.*?(?=\n)', '', content)
    content = re.sub(r'chaptererror;.*?(?=\n)', '', content)
    content = re.sub(r'需要订阅.*?(?=\n)', '', content)
    content = re.sub(r'付费章节.*?(?=\n)', '', content)
    content = re.sub(r'您还没有登录.*?(?=\n)', '', content)
    content = re.sub(r'请登录后在继续阅读本部小说！.*?(?=\n)', '', content)
    content = re.sub(r'广告.*?(?=\n)', '', content)
    content = re.sub(r'https?://[\w\-\.]+(\.[\w\-\.]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', '', content)
    content = content.strip()
    
    if not content:
        print("内容为空")
        return False
    
    # 保存章节
    safe_title = re.sub(r'[\\/:*?"<>|]', '', chapter_title)
    filename = f"{OUTPUT_DIR}/{chapter_index:04d}_{safe_title}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{chapter_title}\n\n{content}")
        print(f"保存成功: {filename}")
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def main():
    print(f"开始从 mayiwsk.com 爬取《{NOVEL_NAME}》...")
    
    # 获取已存在的章节
    existing_chapters = get_existing_chapters()
    print(f"已存在 {len(existing_chapters)} 个章节")
    
    # 获取章节列表
    chapters = get_chapter_list()
    if not chapters:
        print("无法获取章节列表")
        return
    
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 爬取所有章节
    success_count = 0
    failure_count = 0
    
    for i, chapter in enumerate(chapters, 1):
        # 跳过已存在的章节
        if i in existing_chapters:
            print(f"跳过已存在的章节 {i}: {chapter['title']}")
            continue
        
        if download_chapter(chapter, i):
            success_count += 1
        else:
            failure_count += 1
        
        # 随机延迟，避免被反爬
        random_delay()
    
    print(f"\n爬取完成！")
    print(f"成功: {success_count} 个章节")
    print(f"失败: {failure_count} 个章节")
    print(f"已存在: {len(existing_chapters)} 个章节")

if __name__ == "__main__":
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()