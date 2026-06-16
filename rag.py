import json
import numpy as np


# ================= RAG 本地知识库检索核心 =================
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2) if (norm_v1 and norm_v2) else 0

def get_embedding(client, text):
    try:
        response = client.embeddings.create(
            model="embedding-3",
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[-] 获取向量失败: {e}")
        return None

def retrieve_security_knowledge(client, failed_test_info):
    """根据触发的异常信息，去知识库里匹配最相似的安全规范"""
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
    except FileNotFoundError:
        return "警告：未能在本地找到 knowledge_base.json，RAG 检索降级，将依赖模型内部知识。"

    query_vector = get_embedding(client, failed_test_info)
    if not query_vector:
        return "未能检索到相关标准知识。"

    best_match = None
    max_score = -1

    for item in knowledge_base:
        kb_text = f"{item['vulnerability_type']} {item['description']}"
        kb_vector = get_embedding(client, kb_text)

        if kb_vector:
            score = cosine_similarity(query_vector, kb_vector)
            if score > max_score:
                max_score = score
                best_match = item

    if max_score < 0.35 or not best_match:
        return "未能在本地安全库中找到强相关的修复指引。"

    return f"""
【标准漏洞定义】：{best_match['vulnerability_type']}
【标准风险描述】：{best_match['description']}
【行业标准修复建议】：{best_match['remediation']}
"""
