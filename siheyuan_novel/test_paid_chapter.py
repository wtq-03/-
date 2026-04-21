#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试付费章节的访问
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
    'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36'
]

def get_mobile_headers():
    """生成手机端请求头"""
    headers = {
        'User-Agent': random.choice(MOBILE_USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': 'http://wap.faloo.com',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest'
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

# 测试付费章节URL（第499章，应该是付费的）
chapter_url = "http://wap.faloo.com/1238319_499.html"
print(f"测试付费章节访问: {chapter_url}")

# 尝试不同的URL格式
urls_to_try = [
    chapter_url,
    chapter_url + f"?t={int(time.time())}",
    chapter_url + f"?rand={random.randint(1, 100000)}",
    chapter_url.replace('.html', '_old.html'),
    chapter_url.replace('wap.faloo.com', 'b.faloo.com'),
    chapter_url.replace('http://wap.faloo.com', 'https://wap.faloo.com')
]

for i, url in enumerate(urls_to_try, 1):
    print(f"\n尝试 {i}/{len(urls_to_try)}: {url}")
    html = get_html(url)
    if html:
        print(f"页面长度: {len(html)} 字符")
        
        # 检查是否需要登录
        if '您还没有登录' in html:
            print("页面需要登录")
            continue
        
        # 提取内容
        patterns = [
            r'<div class="novel_content">(.*?)</div>',
            r'<div id="content">(.*?)</div>',
            r'<p>(.*?)</p>',
            r'<div class="content">(.*?)</div>',
            r'<div class="article">(.*?)</div>',
            r'<div class="nodeContent">(.*?)</div>',
            r'<div class="read-content">(.*?)</div>'
        ]
        
        content_found = False
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                print(f"找到内容，使用模式: {pattern}")
                # 清理内容
                content = '\n\n'.join(matches)
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
                
                print("提取的内容:")
                print(content[:1000] + "..." if len(content) > 1000 else content)
                content_found = True
                break
        
        if content_found:
            print("\n成功获取付费章节内容！")
            break

if not content_found:
    print("\n所有尝试均未成功获取付费章节内容")
