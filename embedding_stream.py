from sentence_transformers import SentenceTransformer
from rag_chunk import *   # 使用你已有的 chunk 模块


def iter_embedding_stream(txt_path, model_name="all-MiniLM-L6-v2"):
    """
    使用 rag_chunk 生成 chunk，再逐块做 embedding，流式输出。
    """

    # 加载模型（一次即可）
    model = SentenceTransformer(model_name)

    # 逐 chunk 处理
    for idx, chunk in enumerate(iter_chunks_stream(txt_path), start=1):

        # 计算 embedding
        embedding = model.encode(
            chunk,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # 以流式方式返回数据
        yield {
            "id": f"chunk_{idx}",
            "text": chunk,
            "embedding": embedding
        }


if __name__ == "__main__":
    txt_path = "clean_diagnostics.txt"

    # 测试：只看第一个 embedding
    for item in iter_embedding_stream(txt_path):
        print(item["id"])
        print(item["text"], "...\n")
        print(item["embedding"], "\n")
        break
