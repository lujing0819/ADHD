from langchain_core.messages import AIMessage, HumanMessage,ToolMessage
def forget(messages):
    '''
    遗忘messages中的工具类ToolMessage
    '''
    messages=[msg for msg in messages if not isinstance(msg, ToolMessage)]
    messages=[msg for msg in messages if len(msg.content.strip())>0]
    return messages