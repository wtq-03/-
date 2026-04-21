#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium模拟浏览器行为，从番茄小说APP端获取内容
"""

import os
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 小说基础信息
NOVEL_NAME = "四合院：我不爽，都别想好过"
OUTPUT_DIR = "./"

# 番茄小说相关URL
TOMATO_BASE_URL = "https://fanqienovel.com"

# 随机延迟函数
def random_delay(min_delay=2, max_delay=5):
    delay = random.uniform(min_delay, max_delay)
    print(f"等待 {delay:.2f} 秒...")
    time.sleep(delay)

def get_existing_chapters():
    """获取已存在的章节编号"""
    existing = set()
    if os.path.exists(OUTPUT_DIR):
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith('.txt'):
                match = re.match(r'(\d{4})_.*\.txt', filename)
                if match:
                    existing.add(int(match.group(1)))
    return existing

def get_chrome_options():
    """获取Chrome浏览器选项"""
    options = Options()
    # 模拟移动设备
    mobile_emulation = {
        "deviceName": "iPhone X"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    # 无头模式
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 随机用户代理
    user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Fanqie/7.1.5',
        'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0 Fanqie/7.1.5',
        'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36 Fanqie/7.1.5'
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    return options

def search_novel(driver):
    """搜索小说"""
    print(f"在番茄小说网搜索《{NOVEL_NAME}》...")
    
    # 打开番茄小说网
    driver.get(TOMATO_BASE_URL)
    random_delay(3, 5)
    
    # 找到搜索框并输入小说名
    try:
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="书名或作者名"]'))
        )
        search_box.send_keys(NOVEL_NAME)
        random_delay(1, 2)
        
        # 按回车键搜索
        search_box.submit()
        random_delay(3, 5)
        
        # 等待搜索结果加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # 保存当前页面
        with open('tomato_selenium_search.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("搜索结果已保存到 tomato_selenium_search.html")
        
        # 尝试找到小说链接
        novel_links = []
        # 尝试不同的选择器
        selectors = [
            'a[href*="/book/"]',
            'a[href*="/novel/"]',
            'a[href*="/read/"]'
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                title = element.text.strip()
                href = element.get_attribute('href')
                if NOVEL_NAME in title and href:
                    novel_links.append({
                        'title': title,
                        'url': href
                    })
                    print(f"找到小说: {title}")
                    print(f"小说URL: {href}")
        
        return novel_links
        
    except Exception as e:
        print(f"搜索小说时出错: {e}")
        return []

def get_chapter_list(driver, novel_url):
    """获取章节列表"""
    print(f"获取章节列表...")
    
    driver.get(novel_url)
    random_delay(3, 5)
    
    # 等待页面加载
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    
    # 保存章节列表页面
    with open('tomato_selenium_chapters.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("章节列表已保存到 tomato_selenium_chapters.html")
    
    # 尝试找到章节链接
    chapters = []
    # 尝试不同的选择器
    selectors = [
        'a[href*="/chapter/"]',
        'a[href*="/read/"]',
        'a[href*="/content/"]',
        'a[href*="/book/"]'
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            title = element.text.strip()
            href = element.get_attribute('href')
            if '章' in title and href:
                chapters.append({
                    'title': title,
                    'url': href
                })
    
    # 去重并按章节号排序
    seen = set()
    unique_chapters = []
    for chapter in chapters:
        if chapter['url'] not in seen:
            seen.add(chapter['url'])
            unique_chapters.append(chapter)
    
    # 尝试按章节号排序
    def get_chapter_num(title):
        match = re.search(r'第(\d+)章', title)
        return int(match.group(1)) if match else 0
    
    unique_chapters.sort(key=lambda x: get_chapter_num(x['title']))
    print(f"找到 {len(unique_chapters)} 个章节")
    return unique_chapters

def simulate_ad_watch():
    """模拟看广告"""
    print("正在模拟看广告...")
    # 模拟广告观看时间
    ad_time = random.uniform(3, 8)
    print(f"观看广告 {ad_time:.1f} 秒...")
    time.sleep(ad_time)
    print("广告观看完成，获得免费阅读权限！")

def download_chapter(driver, chapter, chapter_index):
    """下载单个章节"""
    chapter_url = chapter['url']
    chapter_title = chapter['title']
    
    print(f"\n下载章节 {chapter_index}: {chapter_title}")
    print(f"URL: {chapter_url}")
    
    # 模拟看广告获取免费权限
    simulate_ad_watch()
    
    # 尝试访问章节页面
    driver.get(chapter_url)
    random_delay(3, 5)
    
    # 等待页面加载
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    
    # 尝试找到内容容器
    content = None
    # 尝试不同的选择器
    selectors = [
        '.novel_content',
        '#content',
        '.content',
        '.article',
        '.read-content',
        '.chapter-content'
    ]
    
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            content = elements[0].text
            break
    
    if not content:
        print("无法获取章节内容")
        return False
    
    # 清理内容
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
    content = re.sub(r'广告.*?(?=\n)', '', content)
    content = content.strip()
    
    if not content:
        print("内容为空")
        return False
    
    # 保存章节
    safe_title = re.sub(r'[\\/:*?"<>|]', '', chapter_title)
    filename = f"{OUTPUT_DIR}/{chapter_index:04d}_{safe_title}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{chapter_title}\n\n{content}")
        print(f"保存成功: {filename}")
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def main():
    print(f"开始从番茄小说APP端爬取《{NOVEL_NAME}》...")
    
    # 获取已存在的章节
    existing_chapters = get_existing_chapters()
    print(f"已存在 {len(existing_chapters)} 个章节")
    
    # 初始化浏览器
    print("初始化浏览器...")
    options = get_chrome_options()
    driver = webdriver.Chrome(options=options)
    
    try:
        # 搜索小说
        novels = search_novel(driver)
        if not novels:
            print("无法找到小说")
            return
        
        # 获取第一个搜索结果
        novel = novels[0]
        print(f"\n选择小说: {novel['title']}")
        print(f"小说URL: {novel['url']}")
        
        # 获取章节列表
        chapters = get_chapter_list(driver, novel['url'])
        if not chapters:
            print("无法获取章节列表")
            return
        
        # 创建输出目录
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        # 爬取所有章节
        success_count = 0
        failure_count = 0
        
        for i, chapter in enumerate(chapters, 1):
            # 跳过已存在的章节
            if i in existing_chapters:
                print(f"跳过已存在的章节 {i}: {chapter['title']}")
                continue
            
            if download_chapter(driver, chapter, i):
                success_count += 1
            else:
                failure_count += 1
            
            # 随机延迟，避免被反爬
            random_delay()
        
        print(f"\n爬取完成！")
        print(f"成功: {success_count} 个章节")
        print(f"失败: {failure_count} 个章节")
        print(f"已存在: {len(existing_chapters)} 个章节")
        
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    main()