#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试搜索番茄小说网
"""

import urllib.request
import http.cookiejar
import gzip
from io import BytesIO
import re
import time
import random

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
        'User-Agent': random.choice(MOBILE_USER_AGENTS),
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

# 尝试访问番茄小说网（番茄小说的域名可能是 fanqienovel.com 或其他）
print("尝试访问番茄小说网...")
tomato_urls = [
    'https://fanqienovel.com',
    'https://m.fanqienovel.com',
    'https://fanqie.com',
    'https://m.fanqie.com'
]

for url in tomato_urls:
    print(f"\n尝试访问: {url}")
    html = get_html(url)
    if html:
        print(f"成功访问，页面长度: {len(html)} 字符")
        # 检查页面标题
        title_match = re.search(r'<title>(.*?)</title>', html)
        if title_match:
            print(f"页面标题: {title_match.group(1)}")
        # 打印页面开头部分
        print("页面开头:")
        print(html[:1000])
        break

print("\n\n尝试搜索小说 '四合院'...")
search_url = "https://m.fanqienovel.com/search"
search_html = get_html(search_url)
if search_html:
    print(f"搜索页面长度: {len(search_html)} 字符")
    print("搜索页面开头:")
    print(search_html[:1000])
