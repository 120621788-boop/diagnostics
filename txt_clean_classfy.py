import jieba
from collections import Counter
import re

def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()

def preprocess_line(line):
    # 去掉数字、标点、特殊符号
    line = re.sub(r"[0-9０-９.,;:：，。、《》【】\[\]\(\)（）\-—…·•!?！？~\s]+", " ", line)
    return line

def build_word_dict(txt_path, min_len=2):
    counter = Counter()

    for raw_line in load_text(txt_path):
        line = preprocess_line(raw_line)
        if not line:
            continue

        # jieba 分词
        words = jieba.lcut(line)

        # 累计词频
        for w in words:
            if len(w) >= min_len:  # 小于2字通常无意义
                counter[w] += 1

    return counter


if __name__ == "__main__":
    txt_path = "clean_diagnostics.txt"

    print("开始分词统计……")
    freq = build_word_dict(txt_path)

    # 输出前 1000 个高频词 ， 观察数据
    print("\n=== Top 高频词（人工筛选无用词的起点） ===\n")
    for word, count in freq.most_common(1000):
        print(word, count)
