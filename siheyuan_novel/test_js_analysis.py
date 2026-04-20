#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析页面JavaScript，寻找内容加载机制
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

# 测试章节页面（第499章）
url = "http://wap.faloo.com/1238319_499.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://wap.faloo.com/booklist/1238319.html',
    'Upgrade-Insecure-Requests': '1'
}

req = urllib.request.Request(url, headers=headers)
try:
    with opener.open(req, timeout=15) as response:
        content = response.read()
        
        # 处理gzip压缩
        content_encoding = response.getheader('Content-Encoding')
        if content_encoding and 'gzip' in content_encoding:
            buf = BytesIO(content)
            with gzip.GzipFile(fileobj=buf) as f:
                content = f.read()
        
        # 解码页面
        html = content.decode('gbk', errors='ignore')
        
        # 提取所有JavaScript文件链接
        js_links = re.findall(r'<script[^>]+src="([^"]+)"[^>]*>', html)
        print("找到的JavaScript文件:")
        for js_link in js_links:
            if js_link.startswith('//'):
                js_link = 'http:' + js_link
            print(f"- {js_link}")
        
        # 提取内联JavaScript
        inline_js = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
        print("\n内联JavaScript:")
        for i, js in enumerate(inline_js):
            if js.strip():
                print(f"\n--- 内联JS {i+1} ---")
                print(js.strip())
        
        # 提取隐藏字段
        hidden_fields = re.findall(r'<input type="hidden" id="([^"]+)" value="([^"]+)" />', html)
        print("\n隐藏字段:")
        for field_name, field_value in hidden_fields:
            print(f"- {field_name}: {field_value}")
            
        # 尝试查找API调用
        api_patterns = [
            r'\$\.ajax\([^)]+\)',
            r'fetch\([^)]+\)',
            r'axios\.[^\(]+\([^)]+\)',
            r'\.get\([^)]+\)',
            r'\.post\([^)]+\)'
        ]
        print("\n可能的API调用:")
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                print(f"- {match.strip()}")
                
        # 尝试访问page2021.js文件，看看内容加载逻辑
        page_js_url = "http://wap.faloo.com/js/newWap/page2021.js"
        print(f"\n尝试获取 page2021.js 文件...")
        try:
            js_req = urllib.request.Request(page_js_url, headers=headers)
            with opener.open(js_req, timeout=15) as js_response:
                js_content = js_response.read()
                js_html = js_content.decode('utf-8', errors='ignore')
                # 查找内容加载相关的代码
                content_load_patterns = [
                    r'loadContent[^\{]+\{[\s\S]*?\}',
                    r'getContent[^\{]+\{[\s\S]*?\}',
                    r'fetchContent[^\{]+\{[\s\S]*?\}',
                    r'nodeContent[^\{]+\{[\s\S]*?\}'
                ]
                print("\n内容加载相关代码:")
                for pattern in content_load_patterns:
                    matches = re.findall(pattern, js_html, re.DOTALL)
                    for match in matches[:2]:  # 只显示前2个匹配
                        print(f"\n--- 匹配 ---\n{match.strip()[:1000]}...")
        except Exception as e:
            print(f"获取 page2021.js 失败: {e}")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
