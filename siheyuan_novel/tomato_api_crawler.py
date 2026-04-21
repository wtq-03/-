#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过番茄小说APP端API获取内容
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

# 番茄小说API相关
API_BASE_URL = "https://novel.douyin.com"
SEARCH_API = "https://novel.douyin.com/api/search/search"
CHAPTER_API = "https://novel.douyin.com/api/chapter/list"
CONTENT_API = "https://novel.douyin.com/api/chapter/content"

# 番茄小说APP用户代理
APP_USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Fanqie/7.1.5',
    'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0 Fanqie/7.1.5',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36 Fanqie/7.1.5',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Mobile/15E148 Fanqie/7.1.5'
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
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': 'https://fanqienovel.com',
        'Origin': 'https://fanqienovel.com',
        'Content-Type': 'application/json',
        # APP特有的请求头
        'X-Requested-With': 'XMLHttpRequest',
        'Fanqie-App-Version': '7.1.5',
        'Fanqie-Platform': 'iOS',
        'Fanqie-Device-Id': f'device_{random.randint(10000000, 99999999)}',
        'X-Tt-Token': '',  # 可以留空，系统会自动生成
        'X-Tt-Env': 'production'
    }
    return headers

def get_json(url, data=None, retry=3):
    """获取JSON数据"""
    for attempt in range(retry):
        try:
            headers = get_app_headers()
            if data:
                data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers=headers)
            else:
                req = urllib.request.Request(url, headers=headers)
            
            with opener.open(req, timeout=20) as response:
                # 处理gzip压缩
                content_encoding = response.getheader('Content-Encoding')
                content = response.read()
                
                if content_encoding and 'gzip' in content_encoding:
                    buf = BytesIO(content)
                    with gzip.GzipFile(fileobj=buf) as f:
                        content = f.read()
                
                # 解析JSON
                try:
                    return json.loads(content.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"响应内容: {content[:500]}")
                    return None
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
    print(f"通过API搜索《{NOVEL_NAME}》...")
    
    # 构建搜索数据
    search_data = {
        "keyword": NOVEL_NAME,
        "page": 1,
        "page_size": 20,
        "type": 1  # 1=小说
    }
    
    print(f"搜索关键词: {NOVEL_NAME}")
    result = get_json(SEARCH_API, search_data)
    
    if not result:
        print("无法获取搜索结果")
        return []
    
    print(f"API响应: {json.dumps(result, indent=2)[:500]}...")
    
    # 提取小说信息
    novels = []
    if result.get('code') == 200:
        data = result.get('data', {})
        books = data.get('books', [])
        
        print(f"找到 {len(books)} 本相关小说")
        
        for book in books:
            book_name = book.get('book_name', '')
            book_id = book.get('book_id', '')
            author = book.get('author_name', '')
            
            if NOVEL_NAME in book_name:
                novels.append({
                    'title': book_name,
                    'author': author,
                    'book_id': book_id
                })
                print(f"找到小说: {book_name} by {author}")
                print(f"小说ID: {book_id}")
    
    return novels

def get_chapter_list(book_id):
    """获取章节列表"""
    print(f"获取章节列表...")
    
    # 构建章节列表请求
    chapter_data = {
        "book_id": book_id,
        "page": 1,
        "page_size": 100  # 一次获取100章
    }
    
    result = get_json(CHAPTER_API, chapter_data)
    
    if not result:
        print("无法获取章节列表")
        return []
    
    print(f"章节API响应: {json.dumps(result, indent=2)[:300]}...")
    
    # 提取章节信息
    chapters = []
    if result.get('code') == 200:
        data = result.get('data', {})
        chapter_list = data.get('chapter_list', [])
        
        print(f"找到 {len(chapter_list)} 个章节")
        
        for chapter in chapter_list:
            chapter_id = chapter.get('chapter_id', '')
            chapter_title = chapter.get('chapter_title', '')
            word_count = chapter.get('word_count', 0)
            
            if chapter_title and '章' in chapter_title:
                chapters.append({
                    'chapter_id': chapter_id,
                    'title': chapter_title,
                    'word_count': word_count
                })
    
    # 按章节顺序排序
    chapters.sort(key=lambda x: x['chapter_id'])
    return chapters

def simulate_ad_watch():
    """模拟看广告"""
    print("正在模拟看广告...")
    # 模拟广告观看时间
    ad_time = random.uniform(3, 8)
    print(f"观看广告 {ad_time:.1f} 秒...")
    time.sleep(ad_time)
    print("广告观看完成，获得免费阅读权限！")

def get_chapter_content(book_id, chapter_id):
    """获取章节内容"""
    # 构建内容请求
    content_data = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "with_ad": True,  # 标记为看广告获取
        "ad_watched": True  # 标记广告已观看
    }
    
    result = get_json(CONTENT_API, content_data)
    
    if not result:
        print("无法获取章节内容")
        return None
    
    if result.get('code') == 200:
        data = result.get('data', {})
        content = data.get('content', '')
        return content
    else:
        print(f"获取内容失败: {result.get('message', '未知错误')}")
        return None

def download_chapter(chapter, chapter_index, book_id):
    """下载单个章节"""
    chapter_id = chapter['chapter_id']
    chapter_title = chapter['title']
    
    print(f"\n下载章节 {chapter_index}: {chapter_title}")
    print(f"章节ID: {chapter_id}")
    
    # 模拟看广告获取免费权限
    simulate_ad_watch()
    
    # 获取章节内容
    content = get_chapter_content(book_id, chapter_id)
    
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
    print(f"开始从番茄小说APP端API爬取《{NOVEL_NAME}》...")
    
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
    print(f"作者: {novel['author']}")
    print(f"小说ID: {novel['book_id']}")
    
    # 获取章节列表
    chapters = get_chapter_list(novel['book_id'])
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
        
        if download_chapter(chapter, i, novel['book_id']):
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
    main()