
from qwen_config import llm
 
import os
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
import os
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from utils import message_to_role_content
os.environ["TAVILY_API_KEY"] = "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"
 



class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 初始化工具
tool = TavilySearch(max_results=2)
tools = [tool]
#result=tool.invoke("今天北京的天气")  # 预热工具，确保首次调用时响应更快

user_id="123"
agent_id="agent_001"

 


# profile_abstract = read_summary(user_id=user_id)
# system_prompt = """你是一个儿童阿斯伯格症状分析助手，专门帮助孩子走出困境。
# 这是孩子的用户画像：{profile_abstract}。
# 请根据这个画像和孩子聊天，帮助孩子更好地表达自己，并提供一些建议。
# 因为是聊天场景，回复尽可能简单明了，适合孩子理解，尽量不要超过20个字。"""
 
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=""   
)

# ---------- 主对话循环 ----------
messages = []          # 当前会话的消息历史
prev_msg_count = 0      # 上一轮的消息总数，用于增量记录

initial_state={"messages": messages}  # 初始状态只包含消息历史，后续会动态添加工具调用结果等上下文  
print ("aaa")
while True:
    user_input = input("请输入表达：")
    if user_input.lower() == "exit":
        break
    # 构造状态并调用 agent（假设 agent 已定义）
    user_msg = HumanMessage(content=user_input)

    # knowledge_message = search_memory(user_id=user_id, query=user_input)   
    # if knowledge_message:
    #     initial_state["messages"].append(HumanMessage(content=f"相关对话知识记忆：{knowledge_message}"))

    # recent_session = read_session_log(user_id=user_id)
    # if recent_session:
    #     initial_state["messages"].extend(recent_session)


    initial_state = {"messages": messages + [user_msg]}
    final_state = agent.invoke(initial_state)   
    updated_messages = final_state["messages"]
    last_message = updated_messages[-1]
    print("助手回复：", last_message.content)
    new_messages = updated_messages[prev_msg_count:]  # 获取本轮新增的消息
    prev_msg_count = len(updated_messages)  # 更新消息总数
    #print (new_messages)
    for msg in new_messages:
        print (type(msg))
        print (message_to_role_content(msg))
        print ("---"*10)
        print ("\n")
    # 记录日志（只需一行函数调用）
    # prev_msg_count = log_interaction(
    #     session_file=session_file,
    #     user_id=user_id,
    #     user_input=user_input,
    #     assistant_reply=last_message.content,
    #     updated_messages=updated_messages,
    #     prev_msg_count=prev_msg_count
    # )
    # messages = updated_messages   # 更新历史
    # memory_message=[{"role":"user","content":user_input}, {"role":"assistant","content":last_message.content}]
    # t = threading.Thread(target=add_message_to_memory, kwargs={"messages":memory_message, "user_id": user_id})
    # t.start()
