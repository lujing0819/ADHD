import datetime
import json
from memory_config import memory#, m_graph
import os   
from langchain_core.messages import HumanMessage, AIMessage
from qwen_config import llm
def summary_memory(user_id,memory_dir="memory"):
    files = [f for f in os.listdir(memory_dir) if f.startswith(user_id)]  
    files_sorted = sorted(files,key=lambda f: os.path.getmtime(os.path.join(memory_dir, f)),reverse=True)
    accumulated_text = ""
    total_chars = 0
    max_chars = 2000
    for filename in files_sorted:
        filepath = os.path.join(memory_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件 {filename} 失败: {e}")
            continue  # 跳过无法读取的文件，继续下一个

        # 如果当前文件内容加入后仍未达到上限，则全部加入
        if total_chars + len(content) <= max_chars:
            accumulated_text += content
            total_chars += len(content)
        else:
            # 加入部分内容刚好达到上限（如果需要精确控制）
            # 这里选择只加入所需长度的文本，达到上限后立即停止
            remaining = max_chars - total_chars
            accumulated_text += content[:remaining]
            total_chars = max_chars
            break  # 已达到目标，停止读取后续文件
    abstract=llm.invoke(f"{accumulated_text} 根据上述内容，总结用户画像,直接输出用户画像，不要输出其他无关内容").content
    return abstract
# abstract=summary_memory(user_id="123") 
# print (abstract)


def convert_to_langchain_messages(raw_messages):
    """
    将原始消息列表（包含 type 和 content）转换为 LangChain 消息对象列表。
    """
    lc_messages = []
    for msg in raw_messages:
        if msg['type'] == 'human':
            lc_messages.append(HumanMessage(content=msg['content']))
        elif msg['type'] == 'ai':
            lc_messages.append(AIMessage(content=msg['content']))
        else:
            # 可处理其他类型或忽略
            continue
    return lc_messages
def read_session_log(user_id):
    """根据用户id，读取最新且文件大小大于0的session文件"""
    session_files = [f for f in os.listdir("sessions") if f.startswith(user_id) and f.endswith(".jsonl")]
    if not session_files:
        return []
    # 按创建时间倒序排序，最新的在前
    session_files.sort(key=lambda x: os.path.getctime(os.path.join("sessions", x)), reverse=True)
    for file_name in session_files:
        file_path = os.path.join("sessions", file_name)
        if os.path.getsize(file_path) > 0:          # 检查文件大小是否大于0
            with open(file_path, "r", encoding="utf-8") as f:
                messages = convert_to_langchain_messages([json.loads(line) for line in f])
            return messages
    # 所有文件都为空
    return []

 


def add_message_to_memory(messages, user_id):                                                                                                                                                                        
    """将消息添加到记忆中"""
    try:
        memory.add(messages=messages, user_id=user_id)
    except Exception as e:
        print(f"Error adding message to memory: {e}")
    try:
        m_graph.add(messages=messages, user_id=user_id)
    except Exception as e:
        print(f"Error adding message to graph: {e}")
def search_memory(query, user_id, top_k=5):
    """从记忆中搜索相关信息"""
    try:
        memory_results= memory.search(query=query, user_id=user_id, limit=top_k)["results"]
        m_graph_results = m_graph.search(query=query, user_id=user_id, limit=top_k)["relations"]
        memory_results = [f"我之前说过：{res['memory']}" for res in memory_results]
        m_graph_results = [f"我{res['relationship']}{res['destination']}" for res in m_graph_results]
        # # 可以根据需要合并或区分这两部分结果 - 这里简单合并
        # print(f"Memory search results: {memory_results}")
        # print(f"Graph search results: {m_graph_results}")
        results=memory_results + m_graph_results
        return results
    except Exception as e:
        print(f"Error searching memory: {e}")
        return []
# search_results = search_memory(query="我上次和你聊了什么？", user_id="123")
# print (f"Search results: {search_results}")

def serialize_message(msg, user_id, timestamp):
    """将 LangChain 消息对象转换为可 JSON 序列化的字典"""
    msg_dict = {
        "timestamp": timestamp,
        "user_id": user_id,
        "type": msg.type,
        "content": msg.content,
    }
    # 处理工具调用（AIMessage 可能包含 tool_calls）
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        tool_calls = []
        for tc in msg.tool_calls:
            if isinstance(tc, dict):
                tool_calls.append({
                    "id": tc.get("id"),
                    "name": tc.get("name") or tc.get("function", {}).get("name"),
                    "args": tc.get("args") or tc.get("function", {}).get("arguments")
                })
            else:  # 假设是 ToolCall 对象
                tool_calls.append({
                    "id": getattr(tc, "id", None),
                    "name": getattr(tc, "name", None),
                    "args": getattr(tc, "args", None)
                })
        msg_dict["tool_calls"] = tool_calls

    # 工具消息特有的关联 ID
    if hasattr(msg, 'tool_call_id'):
        msg_dict["tool_call_id"] = msg.tool_call_id

    return msg_dict

# ---------- 核心日志函数：记录一次交互 ----------
def log_interaction(session_file, user_id, user_input, assistant_reply,
                    updated_messages, prev_msg_count, date=None, time=None):
    """
    将一次用户-助手交互写入每日日志和会话日志。
    参数：
        session_file       : 已打开的会话日志文件对象
        user_id            : 用户标识
        user_input         : 本轮用户输入
        assistant_reply    : 本轮助手最终回复内容
        updated_messages   : agent 返回的完整消息列表（含历史）
        prev_msg_count     : 之前已有的消息数量（用于提取新增消息）
        date, time         : 可选，若不提供则自动获取当前时间
    返回：
        新的消息计数（len(updated_messages)）
    """
    now = datetime.datetime.now()
    if date is None:
        date = now.strftime("%Y-%m-%d")
    if time is None:
        time = now.strftime("%H:%M:%S")

    # 1. 每日日志（每个用户一个 Markdown 文件）
    daily_log_path = f"memory/{user_id}_{date}.md"
    daily_entry = f"### {time} [用户: {user_id}]\n"
    daily_entry += f"**用户**: {user_input}\n"
    daily_entry += f"**助手**: {assistant_reply}\n\n"
    with open(daily_log_path, "a", encoding="utf-8") as f:
        f.write(daily_entry)

    # 2. 会话日志（JSONL）——只写入新增的消息
    new_messages = updated_messages[prev_msg_count:]
    timestamp_iso = now.isoformat()
    for msg in new_messages:
        msg_dict = serialize_message(msg, user_id, timestamp_iso)
        session_file.write(json.dumps(msg_dict, ensure_ascii=False) + "\n")
    session_file.flush()

    return len(updated_messages)


 