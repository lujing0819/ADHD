from datetime import datetime
def message_to_role_content(message):
    role_map = {
        "AIMessage": "assistant",
        "HumanMessage": "user",
        "SystemMessage": "system",
        "ToolMessage": "tool", 
        "ChatMessage": "chat",
        "AgentMessage": "agent"
    }
    role=role_map.get(message.__class__.__name__, "unknown")
    if role=="tool":
        return {
        "role": role,
        "content": message.content,
        "name":message.name,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return {
        "role": role,
        "content": message.content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }