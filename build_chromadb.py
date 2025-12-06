import chromadb
from chromadb.config import Settings
from embedding_stream import iter_embedding_stream


def build_chroma(txt_path, db_path="./medical_db"):
    """
    将 embedding_stream 的流式 embedding 写入 Chroma 本地数据库
    """
    # 创建持久化客户端
    client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False)
    )

    # 创建（或获取）集合
    collection = client.get_or_create_collection(
        name="medical_chunks",
        metadata={"hnsw:space": "cosine"}
    )

    print("开始构建 Chroma 向量数据库...\n")

    # 逐 chunk embedding 写入数据库
    for item in iter_embedding_stream(txt_path):
        collection.add(
            ids=[item["id"]],
            documents=[item["text"]],
            embeddings=[item["embedding"].tolist()]
        )
        print(f"写入: {item['id']}")

    print("\n Chroma 向量数据库构建完成！")
    print(f" 数据库位置: {db_path}")


if __name__ == "__main__":
    build_chroma("clean_diagnostics.txt")
