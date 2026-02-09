from typing import TypedDict
from langchain_core.vectorstores import VectorStore
class AgentState(TypedDict):
    query: str
    user_name: str
    database_name: str
    category: str
    db: VectorStore
    rewrite_query: str
    retrieved_context: list[str]
    reranked_context: list[str]
    answer: str
    scores: dict = {}