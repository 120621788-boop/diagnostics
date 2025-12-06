import json
import re

import chromadb
from chromadb.config import Settings
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# 1) 初始化 DeepSeek（LLM）
client = OpenAI(
    api_key="sk-b7eed39bc060419ea1751ae35ac2a9e8",
    base_url="https://api.deepseek.com/v1"
)

# 2) 初始化 ChromaDB（RAG 向量数据库）
chroma = chromadb.PersistentClient(
    path="./medical_db",
    settings=Settings(anonymized_telemetry=False)
)
collection = chroma.get_collection("medical_chunks")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# 工具：从LLM输出中提取JSON
def extract_json(text):
    match = re.search(r"\{[\s\S]*?\}", text)
    if not match:
        print("未找到 JSON：", text)
        raise ValueError("LLM 未正确输出 JSON")
    return json.loads(match.group())


# Step 1：LLM 分诊（初步科室）
def llm_route_department(symptom: str):
    prompt = f"""
你是一名三甲医院分诊护士，请根据患者主诉判断挂哪个科室。
严格只输出以下 JSON：

{{
  "department": "科室名称",
  "reason": "简短理由"
}}

患者主诉：{symptom}
    """

    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = res.choices[0].message.content
    print("\n=== Step1 LLM 分诊 ===\n", raw)

    return extract_json(raw)


# Step 2（HyDE）：将自然语言症状改写成医学教材风格用于检索
def rewrite_query(symptom: str):
    prompt = f"""
将以下主诉扩展成一段“疑似教材段落”，用于向量检索。
要求：
- 必须模拟诊断学的语法
- 用病理、生理、临床表现的语言来描述
- 不得包含明确诊断，只能描述症状特征
患者主诉：{symptom}
"""
    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    rewritten = res.choices[0].message.content.strip()
    print("\n=== Step2 HyDE 改写后的检索语句 ===\n", rewritten)
    return rewritten


# Step 3：RAG 检索医学教材依据
def rag_search(query: str, k=5):
    emb = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[emb],
        n_results=k
    )

    docs = results["documents"][0]
    scores = results["distances"][0]

    context = []
    for d, s in zip(docs, scores):
        level = similarity_level(s)
        context.append(f"[{level} | 距离={s:.4f}]\n{d[:600]}")

    final_context = "\n\n".join(context)
    print("\n=== Step3 RAG 检索医学依据 ===\n", final_context)

    return final_context, scores


# Step 4：LLM 综合科室判断 + 医学依据 → 最终诊断解释
def llm_generate_final(symptom: str, dept_info, evidence: str):
    prompt = f"""
你是一名三甲医院专业分诊医生，请严格遵守以下【分诊裁决规则】：
【裁决规则】
1.若医学证据中存在“强相关”（距离 < 0.08）内容 → 必须优先分诊对应的器质性科室
2.若只有“中相关”（0.08~0.12） → 可作为辅助参考，不得排除心血管/呼吸系统疾病
3.若仅存在“弱相关或不相关”（>0.12） → 不得作为确定器质性诊断依据
4.任何出现“胸闷、心慌、活动后加重、濒死感”等信号 → 优先级高于心理科
5.心理科只能作为“排除器质性疾病之后”的备选路径

【患者主诉】
{symptom}
【初步科室判断】
{dept_info}
【医学依据（已按相似度分级）】
{evidence}
请严格输出 JSON：
{{
  "department": "最终科室",
  "reason": "基于上述规则与医学依据的最终解释"
}}
    """

    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw = res.choices[0].message.content
    print("\n=== Step4 LLM 最终解释 ===\n", raw)
    return extract_json(raw)



# 总控函数：一次调用完成完整分诊
def triage(symptom: str):
    step1 = llm_route_department(symptom)

    rewritten = rewrite_query(symptom)

    evidence = rag_search(rewritten)

    final = llm_generate_final(symptom, step1, evidence)

    return {
        "initial_department": step1,
        "rag_evidence": evidence,
        "final_report": final
    }

def similarity_level(distance: float):
    if distance < 0.08:
        return "强相关"
    elif distance < 0.12:
        return "中相关"
    elif distance < 0.20:
        return "弱相关"
    else:
        return "不相关"


# 测试
if __name__ == "__main__":
    result = triage("我最近有点累，尤其是跑步后喘气厉害")
    print("\n最终结构化输出")
    print(json.dumps(result, ensure_ascii=False, indent=2))
