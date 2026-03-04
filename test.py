from mem0 import Memory
import os
from openai import OpenAI
 


# 建议从环境变量读取API Key，避免硬编码
DASHSCOPE_API_KEY = "sk-4cf9f15bceea4afda41607e97d7e5db7"

os.environ["OPENAI_API_KEY"]=DASHSCOPE_API_KEY
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
config = {
    # 嵌入模型部分也需要配置，用于向量化记忆
    "llm": {
        "provider": "openai",
        "config": {
            "model": "qwen-plus",
            "temperature": 0.2,
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-v3",
            "embedding_dims": 1024,
        }
    },
    "vector_store": {
        "provider": "faiss",
        "config": {
            "path": "./faiss_index",      # 索引文件路径
            "embedding_model_dims": 1024,             # 可选，通常会自动获取
        }
    }
}

# 从配置初始化 Mem0
memory= Memory.from_config(config)
print (memory.search("你的职业是什么",user_id="xiaoming"))
# print("Mem0 已配置阿里云 Qwen 模型！")
# messages = [
#     {"role": "user", "content": "你好，我叫小明，今年25岁，是一名软件工程师。"},
#     {"role": "assistant", "content": "你好小明，很高兴认识你！"}
# ]

# # 为 user_id 为 "xiaoming" 的用户添加记忆
# result = memory.add(messages=messages, user_id="xiaoming")
# print (result)
# print (memory.get_all(user_id="xiaoming"))
 