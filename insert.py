import os
 
# 适配LangChain 1.2.10，导入路径正确（无变更，修正可能的拼写错误）
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from qwen_config import llm
# 加载环境变量（需提前创建.env文件，写入OPENAI_API_KEY=你的密钥）

os.environ["DASHSCOPE_API_KEY"]=os.getenv("api_key")

# -------------------------- 步骤1：加载并处理文档 --------------------------
def load_document(file_path):
    """根据文件类型加载文档（支持txt/pdf/docx）"""
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    elif file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("仅支持txt/pdf/docx格式文档")
    # 加载文档并返回文档对象列表
    documents = loader.load()
    return documents

def split_documents(documents):
    """分割文档为小片段（避免Token超限）"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # 每个片段最大Token数（约800汉字）
        chunk_overlap=200,  # 片段重叠部分（保证上下文连贯）
        separators=["\n##", "\n###", "\n", "。", "！", "？", "；", "，"]  # 按手册的标题/标点分割
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"文档分割完成，共生成 {len(split_docs)} 个片段")
    return split_docs

# -------------------------- 步骤2：构建向量库和检索器 --------------------------
def build_vector_db(split_docs, persist_directory="./chroma_db"):
    """将分割后的文档向量化并存储到Chroma向量库"""
    embeddings = DashScopeEmbeddings(model="text-embedding-v3")
    vector_db = Chroma(persist_directory=persist_directory,embedding_function=embeddings)
    #docs = [Document(page_content=data.page_content,metadata=data.metadata) for data in split_docs]
    docs = [Document(page_content=str(data.page_content),metadata=data.metadata) for data in split_docs]
    print ("xxxxx")
    vector_db.add_documents(docs)
    print ("xxxxx")
    vector_db.persist()
    asd
    return vector_db



# -------------------------- 步骤4：问答交互 --------------------------
def rag_qa(qa_chain, question):
    """执行问答并返回结果"""
    result = qa_chain.invoke({"query": question})
    # 提取答案和源文档
    answer = result["result"]
    sources = result["source_documents"]
    
    # 格式化输出
    print("\n=== 回答 ===")
    print(answer)
    print("\n=== 参考文档片段 ===")
    for i, doc in enumerate(sources):
        print(f"\n【片段{i+1}】")
        print(f"来源：{doc.metadata.get('source', '未知')}")
        print(f"内容：{doc.page_content[:200]}...")  # 只显示前200字
    return answer

# -------------------------- 主函数：运行整个流程 --------------------------
if __name__ == "__main__":
    # 替换为你的手册文档路径（txt/pdf/docx均可）
    doc_path="G:\\code\\ADHD\\context\\123\\agent_001\documents\\books\\多动症与抽动症儿童治疗指导手册.txt"
  
    
    # 1. 加载并分割文档
    docs = load_document(doc_path)
    split_docs = split_documents(docs)
    
    # 2. 构建向量库和检索器
    vector_db = build_vector_db(split_docs)
    print ("1aaa")
    # # 3. 搭建RAG链
    # qa_chain = build_rag_chain(retriever)
    # print ("2aaa")
    # # 4. 测试问答
    while True:
        question = input("\n请输入你的问题（输入q退出）：")
        if question.lower() == "q":
            break
        result=vector_db.search(question, search_type="similarity", k=5)
        print (result)