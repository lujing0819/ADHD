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
from mem0 import Memory,AsyncMemory
import concurrent.futures
class Context(ABC):
    """上下文抽象基类，所有具体上下文必须实现读写方法。"""
    
    def __init__(self, userid: str, agentid: str):
        self.userid = userid
        self.agentid = agentid
        # 可用作上下文的唯一标识
        self.context_id = f"{userid}:{agentid}:{self.__class__.__name__}"
        if not os.path.exists("context"):
            os.makedirs("context")
        self.base_dir = Path("context")
        self.user_agent_dir = self.base_dir / userid / agentid

    def create_context_dirs(self,base_dir: str, userid: str, agentid: str) -> None:
        """
        在 base_dir 下创建 userid/agentid/ 目录，
        并在 agentid 目录下创建四个子目录：history, memory, tool, profile。
        如果目录已存在，不会报错。
        """
        base_path = Path(base_dir) / self.userid / self.agentid
        subdirs = ['history', 'memory', 'tool', 'profile']   
        for sub in subdirs:
            target = base_path / sub
            target.mkdir(parents=True, exist_ok=True)  # 自动创建父目录，存在即忽略
            print(f"确保目录存在: {target}")

    def _get_subdir(self, subname: str) -> Path:
        """获取子目录（如 history），如不存在则自动创建。"""
        subdir = self.user_agent_dir / subname
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir

    def _get_latest_file(self, directory: Path) -> Optional[Path]:
        """返回目录中最后修改时间最新的文件，如果没有则返回 None。"""
        files = [f for f in directory.iterdir() if f.is_file()]
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime)

    def _is_within_last_hour(self, file_path: Path) -> bool:
        """判断文件的最后修改时间是否在最近一小时之内。"""
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - mtime
        return delta.total_seconds() < 3600  # 一小时 = 3600 秒

    def _new_file_path(self, directory: Path, prefix: str = "data") -> Path:
        """生成一个新的文件名，基于当前时间戳。"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return directory / f"{prefix}_{timestamp}.log"
    def _read_lines_from_file(self, file_path: Path, max_lines: Optional[int] = None) -> List[str]:
        """
        从文件中读取行，返回去除换行符的非空行列表。
        若 max_lines 为 None，读取全部行；否则只读取最后 max_lines 行（保持原顺序）。
        """
        lines = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if max_lines is None:
                    lines = [line.rstrip("\n") for line in f if line.strip()]
                else:
                    dq = deque(maxlen=max_lines)
                    for line in f:
                        line = line.rstrip("\n")
                        if line:
                            dq.append(line)
                    lines = list(dq)
        except Exception as e:
            # 可根据需要记录日志或忽略
            pass
        return lines


    @abstractmethod
    def read(self, **kwargs) -> Any:
        """读取上下文数据，具体参数由子类定义。"""
        pass
    
    @abstractmethod
    def write(self, **kwargs) -> None:
        """写入上下文数据，具体参数由子类定义。"""
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} userid={self.userid} agentid={self.agentid}>"


class HistoryContext(Context):
    """对话历史上下文，存储消息列表。"""
    
    def __init__(self, userid: str, agentid: str, maxlen: int = 100):
        super().__init__(userid, agentid)
        self.maxlen = maxlen
        self.history_dir = self._get_subdir("history")
    
    def read(self, limit: Optional[int] = 10, **kwargs) -> List[Dict[str, str]]:
        """读取所有历史消息，并按文件修改时间合并返回。"""
        files = [f for f in self.history_dir.iterdir() if f.is_file()]
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        messages = []
        remaining = limit
        for file_path in files:
            # 读取当前文件最后 remaining 行（文件内升序）
            lines = self._read_lines_from_file(file_path, max_lines=remaining)
            if not lines:
                continue
            # 将行解析为消息，并插入到结果列表前面以保持整体升序
            msgs = [json.loads(line) for line in lines]
            messages = msgs + messages
            remaining -= len(msgs)
            if remaining <= 0:
                break
        return messages



    def write(self, message: Dict[str, str], **kwargs) -> None:
        """
        写入一条消息，格式如 {"role": "user", "content": "..."}。
        若超过最大长度，自动移除最早的消息。
        """
        latest = self._get_latest_file(self.history_dir)
        if latest and self._is_within_last_hour(latest):
            target_file = latest
        else:
            target_file = self._new_file_path(self.history_dir, prefix="history")
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")

class MemoryContext(Context):
    """记忆上下文，存储键值对形式的长期记忆。"""
    
    def __init__(self, userid: str, agentid: str):
        super().__init__(userid, agentid)
        # 建议从环境变量读取API Key，避免硬编码
        DASHSCOPE_API_KEY = "sk-4cf9f15bceea4afda41607e97d7e5db7"
        os.environ["OPENAI_API_KEY"]=DASHSCOPE_API_KEY
        os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.memory_dir =self._get_subdir("memory")
    
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
                    "path":   os.path.abspath(self.memory_dir),      # 索引文件路径
                    "embedding_model_dims": 1024,             # 可选，通常会自动获取
                }
            },
        }

        # 从配置初始化 Mem0
        self.memory=  Memory.from_config(config)
        self.tmp_file =self._get_subdir("memory")/ "tmp.txt"
        from concurrent.futures import ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(max_workers=2) 
    def read(self, query,limit=10, **kwargs) -> Any:
        """
        读取记忆。
        :param key: 若指定，返回对应键的值；若为 None，返回全部记忆。
        """
        memory_results= self.memory.search(query=query, user_id=self.userid, limit=limit)["results"]
        return memory_results
    def my_write(self,limit=3) -> None:
        def count_lines(filename):
            """返回文件的行数"""
            with open(filename, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        if count_lines(self.tmp_file) >= limit:   
            with open(self.tmp_file, "r", encoding="utf-8") as f:
                lines=f.readlines()
                lines=[eval(line.strip()) for line in lines if line.strip() and len(line.strip())>0]
                self.memory.add(messages=lines, user_id=self.userid)
            # 清空临时文件
            open(self.tmp_file, "w", encoding="utf-8").close()

    def write(self, message: Dict[str, str], **kwargs) -> None: 
        """写入或更新一个键值对。"""
        with open(self.tmp_file, "a", encoding="utf-8") as f:
            f.write(str(message) + "\n")
        self.executor.submit(self.my_write)
  

class ToolContext(Context):
    """工具调用上下文，记录工具调用历史。"""
    
    def __init__(self, userid: str, agentid: str):
        super().__init__(userid, agentid)
        self._calls: List[Dict[str, Any]] = []
    
    def read(self, limit: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        读取工具调用记录。
        :param limit: 返回最近调用数量，None 表示全部。
        """
        if limit is None:
            return self._calls.copy()
        return self._calls[-limit:]
    
    def write(self, tool_call: Dict[str, Any], **kwargs) -> None:
        """
        记录一次工具调用，包含工具名称、参数、结果等。
        """
        self._calls.append(tool_call)


class ProfileContext(Context):
    """用户画像上下文，存储用户属性信息。"""
    
    def __init__(self, userid: str, agentid: str):
        super().__init__(userid, agentid)
        self._profile: Dict[str, Any] = {}
    
    def read(self, key: Optional[str] = None, **kwargs) -> Any:
        """
        读取画像属性。
        :param key: 若指定，返回对应属性值；若为 None，返回全部画像。
        """
        if key is None:
            return self._profile.copy()
        return self._profile.get(key)
    
    def write(self, key: str, value: Any, **kwargs) -> None:
        """设置或更新画像属性。"""
        self._profile[key] = value


# ========== 可选的管理类，用于统一获取上下文实例 ==========
class ContextManager:
    """上下文管理器，负责创建和缓存上下文实例。"""
    
    def __init__(self):
        self._contexts: Dict[str, Context] = {}
    
    def get_context(self, userid: str, agentid: str, context_type: str) -> Context:
        """
        根据用户ID、代理ID和类型获取上下文实例。
        若不存在则创建新实例（此处简化，均创建新实例，实际可缓存）。
        """
        # 简单工厂模式
        context_class = {
            "history": HistoryContext,
            "memory": MemoryContext,
            "tool": ToolContext,
            "profile": ProfileContext
        }.get(context_type.lower())
        
        if not context_class:
            raise ValueError(f"Unknown context type: {context_type}")
        
        # 生成唯一键用于缓存（可选）
        key = f"{userid}:{agentid}:{context_type}"
        if key not in self._contexts:
            self._contexts[key] = context_class(userid, agentid)
        return self._contexts[key]


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 创建具体上下文
    # history = HistoryContext("user123", "agentA")
    # history.write({"role": "user", "content": "Hello"})
    # history.write({"role": "assistant", "content": "Hi there!"})
    # print("History:", history.read())
    
    memory = MemoryContext("user123", "agentA")
    #{"role":"user","content":user_input}, {"role":"assistant","content":last_message.content}
    memory.write({"role": "user", "content": "你好，我今天的肚子特别疼，请问那里有药店"})
    memory.write({"role": "user", "content": "中国的首都是北京"})
    memory.write({"role": "user", "content": "我现在在上海"})
    print ("aaa")

    #print (memory.memory.get_all(user_id="user123"))
    #print("Memory (name):", memory.read("中国"))
    
    # tool = ToolContext("user123", "agentA")
    # tool.write({"tool": "weather", "args": {"city": "Beijing"}, "result": "Sunny"})
    # print("Tool calls:", tool.read())
    
    # profile = ProfileContext("user123", "agentA")
    # profile.write("language", "zh-CN")
    # print("Profile:", profile.read())
    
    # # 使用管理器
    # manager = ContextManager()
    # ctx1 = manager.get_context("user123", "agentA", "history")
    # ctx1.write({"role": "user", "content": "Another message"})
    # ctx2 = manager.get_context("user123", "agentA", "history")  # 相同键会返回同一个实例（如果有缓存）
    # print("Same instance?", ctx1 is ctx2)  # True 如果缓存生效