
from qwen_config import llm
 
import os
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage
 
from langchain_tavily import TavilySearch
import os
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from mem0 import Memory
from context import HistoryContext,MemoryContext
from langchain_community.embeddings import DashScopeEmbeddings
user_id="123"
agent_id="agent_001"
#"history","memory","tool","profile"
# ctx=HistoryContext(user_id,agent_id)
# result=ctx.read()
# print(result)

# ctx=MemoryContext(user_id,agent_id)
# result=ctx.read("肚子有些疼")
# print(result)
os.environ["DASHSCOPE_API_KEY"] =os.getenv("api_key")
 
embedding_model = DashScopeEmbeddings(model="text-embedding-v3")
vector=embedding_model.embed_query("你好")
print (vector)