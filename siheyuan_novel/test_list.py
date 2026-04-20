#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试章节列表页面
"""

import urllib.request
import http.cookiejar
import gzip
from io import BytesIO

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 访问章节列表
url = "http://wap.faloo.com/booklist/1238319.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://wap.faloo.com',
    'Upgrade-Insecure-Requests': '1'
}

req = urllib.request.Request(url, headers=headers)
try:
    with opener.open(req, timeout=15) as response:
        print(f"HTTP状态码: {response.getcode()}")
        print("响应头:")
        for key, value in response.getheaders():
            print(f"{key}: {value}")
        
        content = response.read()
        print(f"响应内容长度: {len(content)}")
        
        # 处理gzip压缩
        content_encoding = response.getheader('Content-Encoding')
        if content_encoding and 'gzip' in content_encoding:
            print("处理gzip压缩...")
            buf = BytesIO(content)
            with gzip.GzipFile(fileobj=buf) as f:
                content = f.read()
            print(f"解压后长度: {len(content)}")
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                html = content.decode(encoding)
                print(f"使用编码 {encoding} 成功解码")
                print("前5000个字符:")
                print(html[:5000])
                print("\n\n后5000个字符:")
                print(html[-5000:])
                break
            except UnicodeDecodeError:
                print(f"编码 {encoding} 解码失败")
                continue
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
