#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从其他免费小说网站获取内容
"""

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

# 小说基础信息
NOVEL_NAME = "四合院：我不爽，都别想好过"
OUTPUT_DIR = "./"

# 免费小说网站列表
FREE_NOVEL_SITES = [
    {
        "name": "笔趣阁",
        "url": "https://www.biquge5200.cc",
        "search_url": "https://www.biquge5200.cc/modules/article/search.php?searchkey={}"
    },
    {
        "name": "顶点小说",
        "url": "https://www.23us.so",
        "search_url": "https://www.23us.so/modules/article/search.php?searchkey={}"
    },
    {
        "name": "起点中文网",
        "url": "https://www.qidian.com",
        "search_url": "https://www.qidian.com/search?kw={}"
    },
    {
        "name": "红袖添香",
        "url": "https://www.hongxiu.com",
        "search_url": "https://www.hongxiu.com/search?keyword={}"
    }
]

# 创建session
session = requests.Session()
session.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'DNT': '1'
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

def search_novel(site):
    """在指定网站搜索小说"""
    print(f"在{site['name']}搜索《{NOVEL_NAME}》...")
    
    # 构建搜索URL
    search_term = requests.utils.quote(NOVEL_NAME)
    search_url = site['search_url'].format(search_term)
    
    print(f"搜索URL: {search_url}")
    html = get_html(search_url)
    
    if not html:
        print(f"无法获取{site['name']}的搜索结果")
        return None
    
    # 保存搜索结果到文件，方便分析
    with open(f'{site["name"]}_search.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"搜索结果已保存到 {site['name']}_search.html")
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试找到小说链接
    novel_links = []
    
    # 根据不同网站的特点尝试不同的选择器
    if site['name'] == "笔趣阁":
        # 笔趣阁的搜索结果选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if NOVEL_NAME in title and href.startswith('http'):
                novel_links.append({
                    'title': title,
                    'url': href
                })
    elif site['name'] == "顶点小说":
        # 顶点小说的搜索结果选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if NOVEL_NAME in title and href.startswith('http'):
                novel_links.append({
                    'title': title,
                    'url': href
                })
    elif site['name'] == "起点中文网":
        # 起点中文网的搜索结果选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if NOVEL_NAME in title and 'book' in href:
                full_url = f"https://www.qidian.com{href}" if href.startswith('/') else href
                novel_links.append({
                    'title': title,
                    'url': full_url
                })
    elif site['name'] == "红袖添香":
        # 红袖添香的搜索结果选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if NOVEL_NAME in title and 'book' in href:
                full_url = f"https://www.hongxiu.com{href}" if href.startswith('/') else href
                novel_links.append({
                    'title': title,
                    'url': full_url
                })
    
    if novel_links:
        print(f"在{site['name']}找到 {len(novel_links)} 个相关结果")
        for link in novel_links:
            print(f"  - {link['title']}: {link['url']}")
        return novel_links[0]  # 返回第一个结果
    else:
        print(f"在{site['name']}未找到《{NOVEL_NAME}》")
        return None

def get_chapter_list(site_name, novel_url):
    """获取章节列表"""
    print(f"获取{site_name}的章节列表...")
    html = get_html(novel_url)
    
    if not html:
        print("无法获取章节列表")
        return []
    
    # 保存章节列表页面
    with open(f'{site_name}_chapters.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"章节列表已保存到 {site_name}_chapters.html")
    
    # 使用BeautifulSoup解析
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试找到章节链接
    chapters = []
    
    # 根据不同网站的特点尝试不同的选择器
    if site_name == "笔趣阁":
        # 笔趣阁的章节选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if '章' in title and href.startswith('http'):
                chapters.append({
                    'title': title,
                    'url': href
                })
    elif site_name == "顶点小说":
        # 顶点小说的章节选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if '章' in title and href.startswith('http'):
                chapters.append({
                    'title': title,
                    'url': href
                })
    elif site_name == "起点中文网":
        # 起点中文网的章节选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if '章' in title and 'chapter' in href:
                full_url = f"https://www.qidian.com{href}" if href.startswith('/') else href
                chapters.append({
                    'title': title,
                    'url': full_url
                })
    elif site_name == "红袖添香":
        # 红袖添香的章节选择器
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True)
            if '章' in title and 'chapter' in href:
                full_url = f"https://www.hongxiu.com{href}" if href.startswith('/') else href
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
    
    # 尝试不同的内容容器
    content = None
    # 尝试不同的选择器
    selectors = [
        '.content',
        '#content',
        '.novel_content',
        '.article',
        '.read-content',
        '.chapter-content',
        '.txt_cont'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            content = elements[0].get_text(separator='\n\n', strip=True)
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
    print(f"开始从其他免费小说网站爬取《{NOVEL_NAME}》...")
    
    # 获取已存在的章节
    existing_chapters = get_existing_chapters()
    print(f"已存在 {len(existing_chapters)} 个章节")
    
    # 尝试每个网站
    for site in FREE_NOVEL_SITES:
        print(f"\n=== 尝试 {site['name']} ===")
        
        # 搜索小说
        novel = search_novel(site)
        if not novel:
            print(f"在{site['name']}未找到小说，尝试下一个网站...")
            continue
        
        print(f"\n选择小说: {novel['title']}")
        print(f"小说URL: {novel['url']}")
        
        # 获取章节列表
        chapters = get_chapter_list(site['name'], novel['url'])
        if not chapters:
            print(f"在{site['name']}无法获取章节列表，尝试下一个网站...")
            continue
        
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
        
        print(f"\n在{site['name']}爬取完成！")
        print(f"成功: {success_count} 个章节")
        print(f"失败: {failure_count} 个章节")
        print(f"已存在: {len(existing_chapters)} 个章节")
        
        # 如果成功获取了章节，就停止尝试其他网站
        if success_count > 0:
            break
    
    print(f"\n所有网站爬取完成！")

if __name__ == "__main__":
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()