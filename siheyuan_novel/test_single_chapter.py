#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个章节的下载
"""

import urllib.request
import http.cookiejar
import gzip
from io import BytesIO
import re
import time

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 测试章节URL
chapter_url = "http://wap.faloo.com/1238319_65.html"  # 作品相关章节，应该是免费的
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://wap.faloo.com/booklist/1238319.html',
    'Upgrade-Insecure-Requests': '1'
}

print(f"测试章节下载: {chapter_url}")
try:
    req = urllib.request.Request(chapter_url, headers=headers)
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
            
            # 检查是否需要登录
            if '您还没有登录' in html:
                print("页面需要登录")
            else:
                print("页面不需要登录")
            
            # 提取内容
            patterns = [
                r'<div class="novel_content">(.*?)</div>',
                r'<div id="content">(.*?)</div>',
                r'<p>(.*?)</p>',
                r'<div class="content">(.*?)</div>',
                r'<div class="article">(.*?)</div>',
                r'<div class="nodeContent">(.*?)</div>',
            ]
            
            content_found = False
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    print(f"找到内容，使用模式: {pattern}")
                    # 清理内容
                    extracted_content = '\n\n'.join(matches)
                    extracted_content = re.sub(r'<[^>]+>', '', extracted_content)
                    extracted_content = re.sub(r'\s+', '\n\n', extracted_content)
                    extracted_content = re.sub(r'[\r\n]+', '\n\n', extracted_content)
                    print("提取的内容:")
                    print(extracted_content[:500] + "...")
                    content_found = True
                    break
            
            if not content_found:
                print("未找到内容")
                # 显示页面的前1000个字符
                print("页面前1000个字符:")
                print(html[:1000])
                
        except UnicodeDecodeError:
            print("解码失败")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
