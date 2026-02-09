from agents.RAGAgent.RAG_AgentState import AgentState
from tools.LLM_Gateway import embedding_model
import os
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import FAISS
def indexing_agent(state: AgentState)-> AgentState:
    database_name=state['database_name']
    index_file = os.path.join(f"{database_name}/", "index.faiss")
    if os.path.exists(index_file):
        db=FAISS.load_local(
            folder_path=f"{database_name}/",
            embeddings=embedding_model(),
            allow_dangerous_deserialization=True)
        return {"db": db}
    else:
        raise RuntimeError(f"Connection to DataBase:{database_name} Failed!")
        