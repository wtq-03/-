#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单版爬虫，尝试绕过反爬措施下载付费章节
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

# 小说基础信息
NOVEL_NAME = "四合院：我不爽，都别想好过"
BASE_URL = "http://wap.faloo.com"
LIST_URL = "http://wap.faloo.com/booklist/1238319.html"
OUTPUT_DIR = "./"

# 随机用户代理池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 随机延迟函数
def random_delay(min_delay=3, max_delay=7):
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

def get_random_headers():
    """生成随机请求头"""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': BASE_URL,
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }
    return headers

def get_html(url, retry=3):
    """获取页面HTML内容，支持重试和gzip解压"""
    for attempt in range(retry):
        try:
            headers = get_random_headers()
            req = urllib.request.Request(url, headers=headers)
            with opener.open(req, timeout=15) as response:
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

def parse_chapter_list():
    """解析章节列表"""
    print("获取章节列表...")
    # 先访问首页，获取cookie
    homepage = get_html(BASE_URL)
    
    # 再访问章节列表
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

def download_chapter(chapter_url, chapter_title, chapter_index):
    """下载单个章节"""
    print(f"\n下载章节 {chapter_index}: {chapter_title}")
    print(f"URL: {chapter_url}")
    
    # 尝试不同的URL格式
    urls_to_try = [
        chapter_url,
        chapter_url + f"?t={int(time.time())}",  # 添加随机参数
        chapter_url.replace('.html', '_old.html'),  # 旧版格式
        chapter_url.replace('wap.faloo.com', 'b.faloo.com')  # PC版
    ]
    
    content = None
    for url in urls_to_try:
        print(f"尝试 URL: {url}")
        html = get_html(url)
        if not html:
            continue
        
        # 检查是否需要登录
        if '您还没有登录' in html:
            print("页面需要登录，尝试下一个URL...")
            continue
        
        # 提取内容
        patterns = [
            r'<div class="novel_content">(.*?)</div>',
            r'<div id="content">(.*?)</div>',
            r'<p>(.*?)</p>',
            r'<div class="content">(.*?)</div>',
            r'<div class="article">(.*?)</div>',
            r'<div class="nodeContent">(.*?)</div>',
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
    print(f"开始爬取《{NOVEL_NAME}》...")
    
    # 获取已存在的章节
    existing_chapters = get_existing_chapters()
    print(f"已存在 {len(existing_chapters)} 个章节")
    
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
        # 跳过已存在的章节
        if i in existing_chapters:
            print(f"跳过已存在的章节 {i}: {chapter['title']}")
            continue
        
        if download_chapter(chapter['url'], chapter['title'], i):
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
