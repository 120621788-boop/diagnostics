import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# 1. 加载 Chroma 本地数据库
client = chromadb.PersistentClient(
    path="./medical_db",
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection("medical_chunks")

# 2. 加载你的 embedding 模型
model = SentenceTransformer("all-MiniLM-L6-v2")

# 3. 用户提问
query = "胸痛的诊断要点"

# 4. embedding 查询向量
q_emb = model.encode(query).tolist()

# 5. 搜索
results = collection.query(
    query_embeddings=[q_emb],
    n_results=3
)

# 6. 输出结果
print("\n🔍 检索结果：")
for i, doc in enumerate(results["documents"][0], start=1):
    print(f"{i}. {doc}...\n")
