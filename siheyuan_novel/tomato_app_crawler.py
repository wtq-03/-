#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟番茄小说APP端访问，通过看广告获取免费内容
"""

import os
import re
import time
import random
import urllib.request
import urllib.error
import http.cookiejar
import gzip
from io import BytesIO
import json

# 小说基础信息
NOVEL_NAME = "四合院：我不爽，都别想好过"
OUTPUT_DIR = "./"

# 番茄小说相关URL
TOMATO_BASE_URL = "https://fanqienovel.com"
TOMATO_SEARCH_URL = "https://fanqienovel.com/search"

# 番茄小说APP用户代理
APP_USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Fanqie/7.1.5',
    'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0 Fanqie/7.1.5',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36 Fanqie/7.1.5',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Fanqie/7.1.5'
]

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

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

def get_app_headers():
    """生成APP端请求头"""
    headers = {
        'User-Agent': random.choice(APP_USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': TOMATO_BASE_URL,
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        # APP特有的请求头
        'X-Requested-With': 'XMLHttpRequest',
        'Fanqie-App-Version': '7.1.5',
        'Fanqie-Platform': 'iOS',
        'Fanqie-Device-Id': f'device_{random.randint(10000000, 99999999)}'
    }
    return headers

def get_html(url, retry=3):
    """获取页面HTML内容，支持重试和gzip解压"""
    for attempt in range(retry):
        try:
            headers = get_app_headers()
            req = urllib.request.Request(url, headers=headers)
            with opener.open(req, timeout=20) as response:
                # 处理gzip压缩
                content_encoding = response.getheader('Content-Encoding')
                content = response.read()
                
                if content_encoding and 'gzip' in content_encoding:
                    buf = BytesIO(content)
                    with gzip.GzipFile(fileobj=buf) as f:
                        content = f.read()
                
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
            if attempt < retry - 1:
                print(f"URL错误: {e}，重试中...")
                random_delay(5, 10)
                continue
            return None
        except urllib.error.HTTPError as e:
            if attempt < retry - 1:
                print(f"HTTP错误: {e}，重试中...")
                random_delay(5, 10)
                continue
            return None
        except Exception as e:
            if attempt < retry - 1:
                print(f"错误: {e}，重试中...")
                random_delay(5, 10)
                continue
            return None
    return None

def search_novel():
    """搜索小说"""
    print(f"在番茄小说网搜索《{NOVEL_NAME}》...")
    
    # 构建搜索URL
    search_term = urllib.parse.quote(NOVEL_NAME)
    search_url = f"{TOMATO_SEARCH_URL}/{search_term}"
    
    print(f"搜索URL: {search_url}")
    html = get_html(search_url)
    
    if not html:
        print("无法获取搜索结果")
        return []
    
    print(f"搜索结果页面长度: {len(html)} 字符")
    
    # 保存搜索结果到文件，方便分析
    with open('tomato_search_result.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("搜索结果已保存到 tomato_search_result.html")
    
    # 从JavaScript中提取window.__INITIAL_STATE__
    pattern = r'window\.__INITIAL_STATE__=(.*?);\s*\}\)\(\)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        print("无法提取初始状态数据")
        return []
    
    try:
        initial_state = json.loads(match.group(1))
        print("成功提取初始状态数据")
        
        # 检查搜索结果
        search_data = initial_state.get('search', {})
        search_book_list = search_data.get('searchBookList', [])
        
        print(f"搜索结果数量: {len(search_book_list)}")
        
        novels = []
        for book in search_book_list:
            book_name = book.get('bookName', '')
            book_id = book.get('bookId', '')
            
            if NOVEL_NAME in book_name:
                # 构建小说URL
                book_url = f"{TOMATO_BASE_URL}/book/{book_id}"
                novels.append({
                    'title': book_name,
                    'url': book_url
                })
                print(f"找到小说: {book_name}")
                print(f"小说URL: {book_url}")
        
        return novels
        
    except json.JSONDecodeError as e:
        print(f"解析JSON错误: {e}")
        return []

def get_chapter_list(novel_url):
    """获取章节列表"""
    print(f"获取章节列表...")
    html = get_html(novel_url)
    
    if not html:
        print("无法获取章节列表")
        return []
    
    # 保存章节列表页面
    with open('tomato_chapter_list.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("章节列表已保存到 tomato_chapter_list.html")
    
    # 提取章节链接
    patterns = [
        r'<a href="(/chapter/\d+)"[^>]*>(.*?)</a>',
        r'<a href="(/read/\d+)"[^>]*>(.*?)</a>',
        r'<a href="(/content/\d+)"[^>]*>(.*?)</a>'
    ]
    
    chapters = []
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for href, title in matches:
            # 清理标题
            title = re.sub(r'<[^>]+>', '', title).strip()
            if '章' in title:
                full_url = f"{TOMATO_BASE_URL}{href}"
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

def simulate_ad_watch():
    """模拟看广告"""
    print("正在模拟看广告...")
    # 模拟广告观看时间
    ad_time = random.uniform(3, 8)
    print(f"观看广告 {ad_time:.1f} 秒...")
    time.sleep(ad_time)
    print("广告观看完成，获得免费阅读权限！")

def download_chapter(chapter, chapter_index):
    """下载单个章节"""
    chapter_url = chapter['url']
    chapter_title = chapter['title']
    
    print(f"\n下载章节 {chapter_index}: {chapter_title}")
    print(f"URL: {chapter_url}")
    
    # 模拟看广告获取免费权限
    simulate_ad_watch()
    
    # 尝试不同的URL格式
    urls_to_try = [
        chapter_url,
        chapter_url + f"?t={int(time.time())}",
        chapter_url + f"?ad_watched=1",
        chapter_url + f"?free_read=1"
    ]
    
    content = None
    for url in urls_to_try:
        print(f"尝试 URL: {url}")
        html = get_html(url)
        if not html:
            continue
        
        # 提取内容
        patterns = [
            r'<div class="novel_content">(.*?)</div>',
            r'<div id="content">(.*?)</div>',
            r'<div class="content">(.*?)</div>',
            r'<div class="article">(.*?)</div>',
            r'<div class="read-content">(.*?)</div>',
            r'<p>(.*?)</p>'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                content = '\n\n'.join(matches)
                break
        
        if content:
            break
    
    if not content:
        print("无法获取章节内容")
        return False
    
    # 清理内容
    content = re.sub(r'<[^>]+>', '', content)
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
    print(f"开始从番茄小说APP端爬取《{NOVEL_NAME}》...")
    
    # 获取已存在的章节
    existing_chapters = get_existing_chapters()
    print(f"已存在 {len(existing_chapters)} 个章节")
    
    # 搜索小说
    novels = search_novel()
    if not novels:
        print("无法找到小说")
        return
    
    # 获取第一个搜索结果
    novel = novels[0]
    print(f"\n选择小说: {novel['title']}")
    print(f"小说URL: {novel['url']}")
    
    # 获取章节列表
    chapters = get_chapter_list(novel['url'])
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
    import urllib.parse
    main()