import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# ================= 配置区 =================
# 填入你申请的大模型 API Key 和基础 URL
API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("BASE_URL")

if not API_KEY:
    raise ValueError("未找到 API_KEY，请检查 .env 文件！")

# 在你的客户端初始化里使用变量
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
