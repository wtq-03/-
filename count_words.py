import os

def count_words_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return len(content)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def main():
    directory = "/workspace/siheyuan_fanfiction_new/第1卷 四合院风云"
    files = os.listdir(directory)
    
    # 筛选前20章
    chapter_files = []
    for file in files:
        if file.startswith("第") and "章" in file and int(file.split("章")[0].replace("第", "")) <= 20:
            chapter_files.append(file)
    
    # 按章节顺序排序
    chapter_files.sort(key=lambda x: int(x.split("章")[0].replace("第", "")))
    
    # 统计字数
    total_words = 0
    print("前20章字数统计：")
    print("-" * 50)
    for file in chapter_files:
        file_path = os.path.join(directory, file)
        word_count = count_words_in_file(file_path)
        total_words += word_count
        print(f"{file}: {word_count} 字")
    
    print("-" * 50)
    print(f"总字数: {total_words} 字")
    print(f"平均每章: {total_words / len(chapter_files):.2f} 字")
    
    # 识别字数不足2000的章节
    print("\n字数不足2000字的章节：")
    for file in chapter_files:
        file_path = os.path.join(directory, file)
        word_count = count_words_in_file(file_path)
        if word_count < 2000:
            print(f"{file}: {word_count} 字")

if __name__ == "__main__":
    main()