from memory_config import memory,m_graph
from user_config import profile
from qwen_config import llm
user_id = profile.user_id
profile=profile.model_dump_json()
profile_abstract=llm.invoke([{"role": "system", "content": f"请根据这个儿童阿斯伯格用户画像，提取出最核心的关键信息，生成一个简短的摘要，要求突出孩子的主要特点和需求，便于快速理解：{profile}"}]).content
 
messages = [
    {"role": "system", "content": "你是一个儿童阿斯伯格症状分析助手，专门帮助孩子走出困境。这是孩子的用户画像：{profile_abstract}。请根据这个画像和孩子聊天，帮助孩子更好地表达自己，并提供一些建议。因为是聊天场景，回复尽可能简单明了，适合孩子理解。"},]
while True:
    user_input = input("请输入表达（输入 'exit' 退出）：")
    if user_input.lower() == "exit":
        break
    user_message={"role": "user", "content": user_input}
    # user_memory = memory.search(user_input, user_id=user_id)
    # print ("用户记忆：",user_memory)
    messages.append(user_message)
    response = llm.invoke(messages)
    print("助手回复：", response.content)
    ai_message={"role": "assistant", "content": response.content}
    messages.append(ai_message)
    #memory.add(messages=[ai_message], user_id="ai_"+user_id)
    memory.add(messages=[user_message], user_id=user_id)
    m_graph.add(messages=[user_message], user_id=user_id)