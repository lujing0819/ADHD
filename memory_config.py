from mem0 import Memory
import os



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
    },
}

# 从配置初始化 Mem0
memory= Memory.from_config(config)

config = {  
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
    "graph_store": {  
        "provider": "neo4j",  
        "config": {  
            "url": "bolt://localhost:7687",  
            "username": "neo4j",  
            "password": "neo4jneo4j",  
        }  
    },  
}  
  
m_graph = Memory.from_config(config_dict=config)  
 