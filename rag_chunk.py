import re


def iter_clean_lines(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                yield ""
            else:
                # 如果这一行有内容：
                # 用正则把多个空白（空格、制表符等）合并成单个空格，保证格式统一。
                line = re.sub(r"\s+", " ", line)
                # 把清洗后的这一行作为生成器输出
                yield line


def iter_chunks_stream(
        txt_path,
        max_chars=500,
        min_chars=200,
        overlap=80
):
    buffer = ""  # buffer 是当前正在积累的那一块文本（chunk 的候选）

    # 遍历清洗后的每一行（已经统一空白和空行）
    for line in iter_clean_lines(txt_path):

        # ---------- 情况 1：遇到空行 ----------
        if line == "":
            # 如果 buffer 里已经积累的文本长度 ≥ 最小 chunk 长度，
            # 说明可以把当前 buffer 当作一个独立的 chunk 输出。
            if len(buffer) >= min_chars:
                # 去掉首尾空白，把 chunk 交给上游（yield）
                yield buffer.strip()
                # 为了保持语义连续，从旧 buffer 尾部截取 overlap 长度
                # 作为下一个 buffer 的“开头”，防止上下文完全断开。
                buffer = buffer[-overlap:]
            # 如果 buffer 太短，则直接继续累积，暂时不切 chunk
            continue

        # ---------- 情况 2：正常累积内容到 buffer ----------
        # 如果把这一行加进 buffer 之后，长度仍然不超过 max_chars，就直接拼接。
        if len(buffer) + len(line) + 1 <= max_chars:
            buffer += line + " "
        else:
            # ---------- 情况 3：加了这一行会超出 max_chars ----------
            # 先把当前 buffer 作为一个完整 chunk 输出
            yield buffer.strip()

            # 然后构造新的 buffer：
            #   1）旧 buffer 尾部截取 overlap 字符，保证上下文连续
            #   2）再把当前这一行加上去，作为新的内容开始。
            buffer = buffer[-overlap:] + line + " "

    # ---------- 文件读完后的收尾处理 ----------
    # 最后可能还有一段没有输出（buffer 中残余的部分）
    if buffer.strip():
        # 如果 buffer 里还有内容，就把它作为最后一个 chunk 输出
        yield buffer.strip()
