import requests
from bs4 import BeautifulSoup
import os
import zipfile

def get_novel_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取小说名称
    novel_title = '四合院：带着大棚在六零当采购员'  # 从页面标题提取
    
    # 获取章节列表
    chapter_list = []
    
    # 查找章节列表容器
    chapter_container = soup.find('div', class_='chapter-list')
    if not chapter_container:
        # 尝试其他可能的容器
        chapter_container = soup.find('div', id='chapter-list')
    
    if chapter_container:
        chapter_elements = chapter_container.find_all('a')
        print(f'找到 {len(chapter_elements)} 个章节链接')
        for chapter in chapter_elements:
            href = chapter.get('href', '')
            text = chapter.text.strip()
            if href and text:
                chapter_title = text
                chapter_url = href
                if not chapter_url.startswith('http'):
                    chapter_url = 'https://www.erciyan.com' + chapter_url
                chapter_list.append((chapter_title, chapter_url))
    else:
        # 尝试直接查找所有符合模式的链接
        all_links = soup.find_all('a')
        for link in all_links:
            href = link.get('href', '')
            text = link.text.strip()
            if '/book/95134517/' in href and '.html' in href:
                chapter_title = text
                chapter_url = href
                if not chapter_url.startswith('http'):
                    chapter_url = 'https://www.erciyan.com' + chapter_url
                chapter_list.append((chapter_title, chapter_url))
    
    print(f'筛选出 {len(chapter_list)} 个章节链接')
    return novel_title, chapter_list

def get_chapter_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取章节内容
    content_element = soup.find('div', class_='content')
    if content_element:
        content = content_element.text.strip()
    else:
        content = ''
    
    return content

def main():
    novel_url = 'https://www.erciyan.com/book/95134517/'
    novel_title, chapter_list = get_novel_info(novel_url)
    
    # 创建小说目录
    if not os.path.exists(novel_title):
        os.makedirs(novel_title)
    
    # 爬取所有章节
    for i, (chapter_title, chapter_url) in enumerate(chapter_list, 1):
        print(f'正在爬取第{i}章: {chapter_title}')
        content = get_chapter_content(chapter_url)
        
        # 保存章节内容
        chapter_file = os.path.join(novel_title, f'{i:03d}_{chapter_title}.txt')
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(chapter_title + '\n\n')
            f.write(content)
    
    # 压缩小说
    zip_file = f'{novel_title}.zip'
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(novel_title):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, novel_title)
                zf.write(file_path, arcname)
    
    print(f'小说爬取完成，已压缩为: {zip_file}')

if __name__ == '__main__':
    main()