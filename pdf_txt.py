import fitz  # PyMuPDF


def iter_pdf_text(pdf_path):
    """
    逐页读取 PDF，使用生成器避免一次性占用内存。
    返回每页的纯文本（如果是文字版 PDF）。
    """
    doc = fitz.open(pdf_path)

    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text")  # 仅文字版 PDF 有效
            yield page_index + 1, text
    finally:
        doc.close()


def pdf_to_txt(pdf_path, txt_path):
    """
    将 PDF 转为 txt（逐页写入），不在内存中存放整本书。
    """
    with open(txt_path, "w", encoding="utf-8") as f:
        for page_no, text in iter_pdf_text(pdf_path):
            f.write(f"\n===== Page {page_no} =====\n\n")
            f.write(text if text else "[无法提取文本]\n")


if __name__ == "__main__":
    pdf_path = "diagnostics.pdf"
    txt_path = "diagnostics.txt"
    print("开始 PDF → TXT 转换（流式）……")
    pdf_to_txt(pdf_path, txt_path)
    print(f"转换完成：{txt_path}")
