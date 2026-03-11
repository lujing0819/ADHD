
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
from context import ContextList
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
 
#ctx_List=ContextList(["history","memory","tool","profile"],agent_id,user_id)
ctx_List=ContextList(["history","tool"],agent_id,user_id)
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

    initial_state = {"messages": messages + [user_msg]}
    print ("user_input:",user_input)
    final_state = agent.invoke(initial_state)   
    messages=final_state["messages"]
    print ("智能体回复",messages[-1])
    new_messages = messages[prev_msg_count:]  
    ctx_List.write(new_messages)
    prev_msg_count = len(messages)  