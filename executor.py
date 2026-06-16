import requests
import concurrent.futures


# ================= 2. 测试执行与并发断言引擎 =================
def assert_and_request(test_case):
    # 【修复】：从 test_case 中动态获取目标 URL，不再依赖全局变量
    target_url = test_case.get("target_url", "http://httpbin.org/post")
    payload = test_case["payload"]
    test_type = test_case["test_type"]

    print(f"[-] 正在向 {target_url} 执行并发测试: {test_type}")
    try:
        # 使用 target_url 而不是写死的 TARGET_URL
        response = requests.post(target_url, data=payload, timeout=5)
        if response.status_code == 200:
            return {
                "test_type": test_type,
                "payload": payload,
                "target_url": target_url, # 在报告中带上目标，便于溯源
                "status_code": response.status_code,
                "is_risk": True
            }
    except Exception as e:
        print(f"[!] 请求 {target_url} 失败: {e}")
    return None

def run_concurrent_tests(test_cases):
    print("[*] 启动轻量级并发断言引擎...")
    risk_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(assert_and_request, test_cases)
        for res in results:
            if res and res["is_risk"]:
                risk_results.append(res)
    return risk_results
