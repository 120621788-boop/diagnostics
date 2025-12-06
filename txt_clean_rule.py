import re

def is_noisy_line(line):
    """判断该行是否属于噪声，无需保留"""
    # 页码
    if re.match(r"^=+ Page \d+ =+$", line):
        return True
    if re.match(r"^\d{1,4}$", line):  # 单独数字行
        return True

    # 无法识别文本
    if "[无法提取文本]" in line:
        return True

    # 目录类（点线）
    if re.search(r"\.{3,}", line):
        return True

    # 版权、出版社信息
    copyright_keywords = [
        "出版社", "出版", "发行", "印刷", "版权所有",
        "责任编辑", "编委", "主编", "副主编", "版本",
        "CIP", "ISBN", "反馈", "投稿", "人民卫生出版社"
    ]
    if any(k in line for k in copyright_keywords):
        return True

    # 纯英文行（Diagnostics, Zhenduanxue）
    if re.match(r"^[A-Za-z\s]+$", line):
        return True

    # 只有符号
    if re.match(r"^[\W_]+$", line):
        return True

    # 太短
    if len(line.strip()) <= 1:
        return True

    return False


def clean_line(line):
    """对保留行做格式清理"""
    line = line.strip()

    # 删除特殊空格
    line = line.replace("\u2003", "").replace("\u3000", "")

    # 多个空格合并
    line = re.sub(r"\s+", " ", line)

    return line


def clean_file(src, dst):
    with open(src, "r", encoding="utf-8") as fin, \
         open(dst, "w", encoding="utf-8") as fout:

        for raw in fin:
            line = raw.strip()

            # 过滤噪声行
            if is_noisy_line(line):
                continue

            clean = clean_line(line)
            if clean:
                fout.write(clean + "\n")


if __name__ == "__main__":
    clean_file("diagnostics.txt", "clean_diagnostics.txt")
    print("清洗完成 → clean_diagnostics.txt")
