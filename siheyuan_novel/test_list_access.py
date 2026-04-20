#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试章节列表页面的访问情况
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

# 章节列表URL
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

print(f"访问章节列表页面: {url}")
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
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                html = content.decode(encoding)
                print(f"使用编码 {encoding} 成功解码")
                
                # 尝试提取章节链接
                pattern = r'<a href="(//wap\.faloo\.com/1238319_\d+\.html)".*?>(.*?)</a>'
                matches = re.findall(pattern, html, re.DOTALL)
                
                print(f"找到 {len(matches)} 个章节链接")
                for i, (href, title) in enumerate(matches[:10]):  # 只显示前10个
                    print(f"{i+1}. {title.strip()} - {href}")
                
                if len(matches) > 10:
                    print(f"... 还有 {len(matches) - 10} 个章节")
                
                break
            except UnicodeDecodeError:
                print(f"编码 {encoding} 解码失败")
                continue
        
        # 检查是否有反爬措施
        if '验证码' in html or '请输入验证码' in html:
            print("页面包含验证码，可能被反爬")
        elif '访问过于频繁' in html or '请稍后再试' in html:
            print("访问过于频繁，可能被反爬")
        elif '404' in html or '找不到页面' in html:
            print("页面不存在")
        else:
            print("页面访问正常")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
