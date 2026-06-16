import json
import openai


# ================= 1. 接口解析与用例智能生成 =================
def generate_test_cases(client, model_name, target_url, original_params):
    print(f"\n[*] 正在为接口 {target_url} 生成安全测试用例...")
    prompt = rf"""
    你是一个高级 Web 安全攻防专家。我现在准备对以下 HTTP 接口进行深度安全测试：
    目标 URL: {target_url}
    原始正常请求体: {json.dumps(original_params)}

    请针对该接口的特征，生成 6 个高质量的安全测试用例。你的用例必须涵盖以下维度：
    1. SQL 注入 (包含基础的单引号注入或报错注入)
    2. 业务逻辑漏洞 (例如垂直越权、角色篡改)
    3. XSS 跨站脚本攻击
    4. 目录遍历 (Directory Traversal，例如尝试在参数中注入 ../../../etc/passwd)
    5. 命令注入 (Command Injection，例如拼接 | whoami 或 ; id)
    6. 敏感信息泄露 (尝试传入特殊符号导致底层堆栈报错回显)

    【JSON 格式终极红线警告！！！必须严格遵守】：
    1. 只能返回纯 JSON 数组，不要包含 ```json 等任何 Markdown 标记。
    2. JSON 里的所有的值（Value）必须是纯静态的字符串！
    3. 绝对禁止生成任何超长字符串或超长数字！所有 Payload 的长度不得超过 30。
    4. 绝对禁止在 JSON 中使用 +、*、.join() 等任何代码表达式！

    【标准输出范例（请完全照抄这个数据结构格式，并自行扩展至 6 个）】：
    [
        {{
            "test_type": "SQL注入",
            "payload": {{"username": "admin' OR 1=1--", "password": "123"}},
            "expected_risk": "数据库信息泄露"
        }},
        {{
            "test_type": "逻辑越权测试",
            "payload": {{"username": "admin", "password": "123", "role_id": "0"}},
            "expected_risk": "垂直越权"
        }},
        {{
            "test_type": "目录遍历测试",
            "payload": {{"username": "../../../etc/passwd", "password": "123"}},
            "expected_risk": "任意文件读取"
        }}
    ]
    """

    try:
        # 修复了双重调用的 Bug，统一在这个安全的 try 块里执行并加上 max_tokens
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3500,
            timeout=60.0
        )
        print("[+] 成功接收到大模型返回的数据！正在解析...")

        raw_output = response.choices[0].message.content.strip()
        # 清洗可能带有的 Markdown 标记
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3].strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output[3:-3].strip()

        print("\n[*] 大模型返回的原始数据如下：\n" + raw_output + "\n")

        cleaned_output = raw_output.replace('\\', '\\\\')
        return json.loads(cleaned_output)

    except openai.InternalServerError as e:
        print(f"\n[!] 大模型服务器内部错误 (500): {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"[!] JSON 解析彻底失败: {e}")
        print("[-] 大模型本次生成的格式不合规，请重新运行脚本重试。")
        return []
    except Exception as e:
        print(f"\n[!] API 调用或解析出现其他异常: {e}")
        return []
