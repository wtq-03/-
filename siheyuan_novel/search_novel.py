#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在番茄小说网搜索小说
"""

import urllib.request
import urllib.parse
import http.cookiejar
import gzip
from io import BytesIO
import re
import json

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 手机端用户代理
MOBILE_USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0'
]

def get_mobile_headers():
    """生成手机端请求头"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }
    return headers

def get_html(url):
    """获取页面HTML内容"""
    try:
        headers = get_mobile_headers()
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
            return str(content)
    except Exception as e:
        print(f"错误: {e}")
        return None

# 搜索关键词
search_keyword = "四合院 我不爽"

print(f"在番茄小说网搜索: {search_keyword}")

# 构建搜索URL（可能需要尝试不同的搜索方式）
search_url_1 = f"https://fanqienovel.com/search?keyword={urllib.parse.quote(search_keyword)}"
search_url_2 = f"https://fanqienovel.com/search/{urllib.parse.quote(search_keyword)}"
search_url_3 = f"https://m.fanqienovel.com/search?q={urllib.parse.quote(search_keyword)}"

# 尝试不同的搜索URL
search_urls = [search_url_1, search_url_2, search_url_3]

for i, url in enumerate(search_urls, 1):
    print(f"\n尝试搜索 URL {i}: {url}")
    html = get_html(url)
    if html:
        print(f"搜索页面长度: {len(html)} 字符")
        # 查找小说标题或链接
        print("查找小说相关内容...")
        # 查找包含书名的内容
        if '四合院' in html:
            print("找到与'四合院'相关的内容！")
        # 查找小说链接
        book_links = re.findall(r'href="(/page/[0-9]+)"', html)
        if book_links:
            print(f"找到 {len(book_links)} 个小说链接:")
            for link in book_links[:5]:
                print(f"https://fanqienovel.com{link}")
        # 查找书名
        book_titles = re.findall(r'<span class="[^"]*book[^"]*title[^"]*">([^<]+)</span>', html, re.IGNORECASE)
        if book_titles:
            print(f"找到 {len(book_titles)} 个小说标题:")
            for title in book_titles[:10]:
                print(f"  - {title}")
        # 保存搜索页面供分析
        with open('/workspace/siheyuan_novel/search_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("搜索页面已保存到 search_page.html")
        break

print("\n\n尝试搜索更简单的关键词...")
simple_keyword = "四合院"
simple_search_url = f"https://fanqienovel.com/search?keyword={urllib.parse.quote(simple_keyword)}"
simple_html = get_html(simple_search_url)
if simple_html:
    print(f"简单搜索页面长度: {len(simple_html)} 字符")
    if '四合院' in simple_html:
        print("找到与'四合院'相关的内容！")
    # 保存简单搜索页面
    with open('/workspace/siheyuan_novel/simple_search.html', 'w', encoding='utf-8') as f:
        f.write(simple_html)
    print("简单搜索页面已保存到 simple_search.html")
