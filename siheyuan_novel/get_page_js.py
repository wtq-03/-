#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取page2021.js文件的完整内容
"""

import urllib.request
import http.cookiejar
import gzip
from io import BytesIO

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 页面JavaScript文件
url = "http://wap.faloo.com/js/newWap/page2021.js?20240827"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/javascript,application/javascript,application/ecmascript,application/x-ecmascript,*/*;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://wap.faloo.com/1238319_499.html',
    'Upgrade-Insecure-Requests': '1'
}

req = urllib.request.Request(url, headers=headers)
try:
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
        
        # 解码内容
        try:
            js_content = content.decode('utf-8')
            print(f"文件长度: {len(js_content)} 字符")
            print("\n文件内容:")
            print(js_content)
        except UnicodeDecodeError:
            try:
                js_content = content.decode('gbk')
                print(f"文件长度: {len(js_content)} 字符")
                print("\n文件内容:")
                print(js_content)
            except UnicodeDecodeError:
                print("解码失败，显示原始内容:")
                print(content)
                
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
