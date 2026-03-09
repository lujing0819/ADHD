from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import uuid
import os
from pathlib import Path
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
import json
from collections import deque
from mem0 import Memory
os.environ["DASHSCOPE_API_KEY"] = "sk-4cf9f15bceea4afda41607e97d7e5db7"
os.environ["OPENAI_API_KEY"]="sk-4cf9f15bceea4afda41607e97d7e5db7"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
memory_dir ="./faiss_index" #self._get_subdir("memory")

config = {
    # 嵌入模型部分也需要配置，用于向量化记忆
    "llm": {
        "provider": "openai",
        "config": {
            "model": "qwen3.5-plus",
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
            "path":  "./faiss_index",      # 索引文件路径
            "embedding_model_dims": 1024,             # 可选，通常会自动获取
        }
    },
}

# # 从配置初始化 Mem0
memory= Memory.from_config(config)
memory_message=[{"role": "assistant", "content": "中国的首都是哪"}, {"role": "user", "content": "中国的首都是北京"}]
result=memory.add(messages=memory_message, user_id="123",infer=False)
print (result)
#print(memory.get_all(user_id="123"))

# import dashscope
# from http import HTTPStatus
# input_texts = "衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买"

# resp = dashscope.TextEmbedding.call(
# model="text-embedding-v3",
# input=input_texts
# )
# print(len(resp["output"]["embeddings"][0]["embedding"]))