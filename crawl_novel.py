import requests
from bs4 import BeautifulSoup
import os
import zipfile

def get_novel_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 获取小说名称
    novel_title = '四合院：带着大棚在六零当采购员'  # 从页面标题提取
    
    # 获取章节列表
    chapter_list = []
    
    # 具体的分页链接
    page_urls = [
        'https://www.erciyan.com/book/95134517/',      # 1-200章
        'https://www.erciyan.com/book/95134517/2/',    # 201-400章
        'https://www.erciyan.com/book/95134517/3/',    # 401-600章
        'https://www.erciyan.com/book/95134517/4/'     # 601-749+两张番外
    ]
    
    for page_num, page_url in enumerate(page_urls, 1):
        print(f'正在爬取第 {page_num} 页目录: {page_url}')
        
        # 添加错误处理和重试
        max_retries = 3
        response = None
        for retry in range(max_retries):
            try:
                response = requests.get(page_url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                break
            except Exception as e:
                print(f'第 {retry+1} 次尝试失败: {e}')
                if retry == max_retries - 1:
                    print(f'第 {page_num} 页爬取失败，跳过...')
                    continue
        
        if not response:
            continue
        
        # 解析页面
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 直接查找所有章节链接
        all_links = soup.find_all('a')
        page_chapters = 0
        
        for link in all_links:
            href = link.get('href', '')
            text = link.text.strip()
            
            # 过滤条件：
            # 1. 包含小说ID的链接
            # 2. 包含.html
            # 3. 不是javascript链接
            # 4. 包含章节号或番外
            if '/book/95134517/' in href and '.html' in href and 'javascript:' not in href:
                import re
                # 提取章节号
                chapter_match = re.search(r'第(\d+)章', text)
                if chapter_match or '番外' in text:
                    # 构建完整URL
                    if not href.startswith('http'):
                        href = 'https://www.erciyan.com' + href
                    
                    # 添加到章节列表
                    chapter_list.append((text, href))
                    page_chapters += 1
        
        print(f'第 {page_num} 页找到 {page_chapters} 个章节链接')
    
    # 去重，避免重复章节（基于URL去重）
    seen_urls = set()
    unique_chapters = []
    for title, url in chapter_list:
        if url not in seen_urls:
            seen_urls.add(url)
            unique_chapters.append((title, url))
    chapter_list = unique_chapters
    
    # 按章节标题排序
    def sort_key(chapter):
        title = chapter[0]
        import re
        match = re.search(r'第(\d+)章', title)
        if match:
            return int(match.group(1))
        if '番外' in title:
            return 9999
        return 0
    
    chapter_list.sort(key=sort_key)
    
    print(f'总共筛选出 {len(chapter_list)} 个章节链接')
    return novel_title, chapter_list

def get_chapter_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 添加错误处理和重试
    max_retries = 3
    for retry in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            break
        except Exception as e:
            print(f'爬取章节失败（第{retry+1}次尝试）: {e}')
            if retry == max_retries - 1:
                return f'爬取失败: {e}'
            continue
    
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
    
    # 检查已爬取的章节
    existing_chapters = set()
    if os.path.exists(novel_title):
        for file in os.listdir(novel_title):
            if file.endswith('.txt'):
                # 提取章节标题
                title = file.split('_', 1)[1].replace('.txt', '')
                existing_chapters.add(title)
    
    # 爬取未爬取的章节
    for i, (chapter_title, chapter_url) in enumerate(chapter_list, 1):
        if chapter_title in existing_chapters:
            print(f'跳过已爬取的章节: {chapter_title}')
            continue
        
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