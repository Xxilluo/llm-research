import time
from config import client, MODEL_NAME
from loader import load_target_apis
from generator import generate_test_cases
from executor import run_concurrent_tests
from reporter import generate_markdown_report


# ================= 主程序执行流 =================
if __name__ == "__main__":
    start_time = time.time()

    # 1. 一键读取所有的外部接口
    apis = load_target_apis("targets.json")

    all_cases = []
    # 2. 遍历每一个接口，分别找大模型要测试用例
    for api in apis:
        cases = generate_test_cases(client, MODEL_NAME, api["url"], api["params"])
        if cases:
            # 【重要】：必须把 api["url"] 塞进每一个生成的 case 里，否则断言引擎找不到目标
            for case in cases:
                case["target_url"] = api["url"]
            all_cases.extend(cases)

    # 3. 把这个装满用例的弹药箱，一次性倒进并发测试引擎里
    if all_cases:
        risks = run_concurrent_tests(all_cases)
        generate_markdown_report(client, MODEL_NAME, risks)
