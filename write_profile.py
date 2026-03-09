import os
import datetime
from memory_function import summary_memory
user_id_list=os.listdir("profile")
for user_id in user_id_list:
    abstract= summary_memory(user_id=user_id)
    os.makedirs(f"profile\\{user_id}", exist_ok=True)
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    path = f"profile\\{user_id}\\{user_id}_{date}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(abstract)