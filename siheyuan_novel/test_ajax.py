#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AJAX接口获取章节内容
"""

import urllib.request
import http.cookiejar
import gzip
from io import BytesIO
import json
import re

# 创建cookie处理器
cookie_jar = http.cookiejar.CookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie_jar)
opener = urllib.request.build_opener(handler)

# 测试AJAX接口获取章节内容
# 小说ID: 1238319, 章节ID: 499
url = "http://wap.faloo.com/page2020.aspx"
params = {
    'act': 'waterfall',
    'ID': '1238319',
    'n': '499',
    'SourceSub': ''
}

# 构建请求体
data = '&'.join([f"{k}={v}" for k, v in params.items()]).encode('utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://wap.faloo.com/1238319_499.html',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Length': str(len(data))
}

req = urllib.request.Request(url, data=data, headers=headers, method='POST')
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
        
        # 解码内容
        try:
            response_text = content.decode('utf-8')
            print("\n响应内容:")
            print(response_text)
            
            # 尝试解析JSON
            try:
                data = json.loads(response_text)
                print("\n解析JSON成功:")
                print(f"是否有content: {'conment' in data}")
                if 'conment' in data:
                    # 提取内容
                    conment = data['conment']
                    # 清理HTML标签
                    clean_content = re.sub(r'<[^>]+>', '', conment)
                    clean_content = re.sub(r'\s+', '\n\n', clean_content)
                    clean_content = re.sub(r'[\r\n]+', '\n\n', clean_content)
                    print("\n提取的内容:")
                    print(clean_content[:2000])
            except json.JSONDecodeError:
                print("\n响应不是有效的JSON")
        except UnicodeDecodeError:
            try:
                response_text = content.decode('gbk')
                print("\n响应内容:")
                print(response_text)
            except UnicodeDecodeError:
                print("\n解码失败，显示原始内容:")
                print(content)
                
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
