def message_to_role_content(message):
    role_map = {
        "AIMessage": "assistant",
        "HumanMessage": "user",
        "SystemMessage": "system",
        "ToolMessage": "tool", 
        "ChatMessage": "chat",
        "AgentMessage": "agent"
    }
    return {
        "role": role_map.get(message.__class__.__name__, "unknown"),
        "content": message.content
    }