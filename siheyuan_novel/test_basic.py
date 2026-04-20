#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基本的网络访问和章节列表获取功能
"""

import urllib.request
import http.cookiejar
import gzip
from io import BytesIO
import re

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 测试URL
url = "http://wap.faloo.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

print("测试基本网络访问...")
try:
    req = urllib.request.Request(url, headers=headers)
    with opener.open(req, timeout=15) as response:
        print(f"HTTP状态码: {response.getcode()}")
        content = response.read()
        
        # 处理gzip压缩
        content_encoding = response.getheader('Content-Encoding')
        if content_encoding and 'gzip' in content_encoding:
            print("处理gzip压缩...")
            buf = BytesIO(content)
            with gzip.GzipFile(fileobj=buf) as f:
                content = f.read()
        
        # 尝试解码
        try:
            html = content.decode('gbk')
            print(f"页面长度: {len(html)} 字符")
            print("页面标题:")
            title_match = re.search(r'<title>(.*?)</title>', html)
            if title_match:
                print(title_match.group(1))
            print("\n访问成功！")
        except UnicodeDecodeError:
            print("解码失败")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n测试章节列表页面...")
list_url = "http://wap.faloo.com/booklist/1238319.html"
try:
    req = urllib.request.Request(list_url, headers=headers)
    with opener.open(req, timeout=15) as response:
        print(f"HTTP状态码: {response.getcode()}")
        content = response.read()
        
        # 处理gzip压缩
        content_encoding = response.getheader('Content-Encoding')
        if content_encoding and 'gzip' in content_encoding:
            print("处理gzip压缩...")
            buf = BytesIO(content)
            with gzip.GzipFile(fileobj=buf) as f:
                content = f.read()
        
        # 尝试解码
        try:
            html = content.decode('gbk')
            print(f"页面长度: {len(html)} 字符")
            
            # 提取章节链接
            pattern = r'<a href="(//wap\.faloo\.com/1238319_\d+\.html)".*?>(.*?)</a>'
            matches = re.findall(pattern, html, re.DOTALL)
            print(f"找到 {len(matches)} 个章节链接")
            for i, (href, title) in enumerate(matches[:5]):
                title = re.sub(r'<[^>]+>', '', title).strip()
                print(f"{i+1}. {title} - {href}")
            print("\n章节列表获取成功！")
        except UnicodeDecodeError:
            print("解码失败")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
