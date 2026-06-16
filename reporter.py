import json
from rag import retrieve_security_knowledge


# ================= 3. 风险评级与报告自动化 (接入 RAG) =================
def generate_markdown_report(client, model_name, risk_results):
    if not risk_results:
        print("[+] 未发现明显安全风险，无需生成报告。")
        return

    print(f"[*] 检测到 {len(risk_results)} 个异常数据，正在启动 RAG 检索安全知识库...")

    # 将异常结果提取为文本供向量检索
    failed_info_summary = json.dumps(risk_results, ensure_ascii=False)
    raw_knowledge = retrieve_security_knowledge(client, failed_info_summary)

    print("[+] 知识库召回完毕！正在二次调度 LLM 构建 Markdown 风险报告...")

    report_prompt = f"""
    你是一个专业的自动化安全审计专家。请结合【实际测试异常数据】和 RAG 召回的【行业标准规范】，生成一份 Markdown 安全风险报告。

    【实际测试异常数据】：
    {failed_info_summary}

    【RAG 召回的行业标准指引 (必须严格以此为基础编写修复方案)】：
    {raw_knowledge}

    【输出格式】：
    # 智能安全测试风险报告
    - **发现的漏洞与风险**：(简述发生了什么)
    - **复现上下文**：(列出 Payload 和状态码)
    - **行业合规修复方案**：(结合 RAG 召回的数据详细说明)
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": report_prompt}],
            temperature=0.2,
            max_tokens=1500
        )
        report_content = response.choices[0].message.content

        # 写入文件
        report_path = r"C:\Users\XL\Desktop\jianli\Security_Risk_Report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"[√] 完美闭环！融合了 RAG 的风险报告已生成：{report_path}")
    except Exception as e:
        print(f"[!] 报告生成失败: {e}")
