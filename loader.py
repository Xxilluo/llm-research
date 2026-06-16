import json


# 1. 增加一个读取外部文件的函数
def load_target_apis(file_path="targets.json"):
    print(f"[*] 正在加载外部接口定义文件: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] 读取配置文件失败: {e}")
        return []
