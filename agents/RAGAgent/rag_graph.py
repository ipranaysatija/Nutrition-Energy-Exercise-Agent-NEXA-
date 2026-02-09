from tools.LLM_Gateway import nexa_ai,embedding_model
from typing import TypedDict
import pdfplumber
from langchain_core.vectorstores import VectorStore
from  agents.RAGAgent.IndexingAgent import indexing_agent
from agents.RAGAgent.RetrievalAgent import rewrite_query, retrieval_agent
from agents.RAGAgent.AugmentationAgent import augmentation_agent
from agents.RAGAgent.GenerationAgent import generation_agent
from agents.RAGAgent.ReflectionAgent import reflection_agent
from langgraph.graph import StateGraph, START,END
from agents.RAGAgent.RAG_AgentState import AgentState


graph=StateGraph(AgentState)
graph.add_node("indexing_agent", indexing_agent)
graph.add_node("rewrite_query", rewrite_query)
graph.add_node("retrieval_agent", retrieval_agent)
graph.add_node("augmentation_agent", augmentation_agent)
graph.add_node("generation_agent", generation_agent)
graph.add_node("reflection_agent", reflection_agent)

graph.add_edge(START, "indexing_agent")
graph.add_edge("indexing_agent", "rewrite_query")
graph.add_edge("rewrite_query", "retrieval_agent")
graph.add_edge("augmentation_agent", "generation_agent")
graph.add_edge("generation_agent", "reflection_agent")
graph.add_edge("reflection_agent", END)

app = graph.compile()

def rag_chat(query,category,user_name,database_name):
    input_state = {
            "query": query,
            "category":category,
            "user_name":user_name,
            'database_name':database_name
        }
    rag_state=app.invoke(input_state)
    return rag_state.get('answer'),rag_state.get('scores',{})
# def rag_chat(path: str):
#     """Function to interact with the RAG agent."""
#     query=""
#     while query.strip() != "exit()":
#         query=input("Enter your query: ")
#         if query.strip() == "exit()":
#             break
#         input_state = {
#             "query": query,
#             "path": path
#         }
#         output_state = app.invoke(input_state)
#         print("Answer:", output_state['answer'], "\nScores:", output_state['scores'])
#     return output_state