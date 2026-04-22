import os

def count_chinese_chars(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 统计中文字符数
    chinese_chars = 0
    for char in content:
        if '\u4e00' <= char <= '\u9fff':
            chinese_chars += 1
    return chinese_chars

# 要统计的文件列表
files = [
    "siheyuan_fanfiction_new/第1卷 四合院风云/第6章 傻柱上门.txt",
    "siheyuan_fanfiction_new/第1卷 四合院风云/第7章 供销社采购.txt",
    "siheyuan_fanfiction_new/第1卷 四合院风云/第8章 贾家作妖.txt",
    "siheyuan_fanfiction_new/第1卷 四合院风云/第9章 医务科立功.txt",
    "siheyuan_fanfiction_new/第1卷 四合院风云/第10章 新能力抽奖.txt"
]

# 统计每个文件的中文字数
for file in files:
    count = count_chinese_chars(file)
    print(f"{file}: {count} 字")
