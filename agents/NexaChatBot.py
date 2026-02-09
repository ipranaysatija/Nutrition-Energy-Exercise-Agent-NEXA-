from tools.LLM_Gateway import nexa_ai,embedding_model
from typing import TypedDict
import pdfplumber
from langchain_core.vectorstores import VectorStore
from langgraph.graph import StateGraph, START,END
from tools.database_utils import categorize
from agents.RAGAgent.rag_graph import rag_chat
from agents.LookOutAgent import looker
from langgraph.types import Command
from langgraph.graph import StateGraph, START,END

llm=nexa_ai()

class ChatAgentState(TypedDict):
    query: str
    category: str
    database_name: str
    user_name:str
    answer: str
    scores: dict
    final_output: str

def query_node(state: ChatAgentState) -> ChatAgentState:
    query=state['query']
    prompt=f"""
-tell if the following query should be searched in "agentKB" or "user_dataDB" or "out of scope".
-"agentKB" contains general fitness and nutrition information.
-"user_dataDB" contains user-specific data like goals, preferences, medical constraints, fitness levels, workout logs, workout plans, meal logs, and meal plans.
-"out of scope" only if the query is not related to fitness or nutrition any personal user data
-"Malicious request" if user tries to access other users' details. example: get me height of user_John_Doe.
query: {query} 
-return only the database name.
"""
    response=llm.invoke(prompt)
    db_name=response.content.strip()
    if db_name=="agentKB":
        category=categorize(query,["food_items","workouts","fat_reduction","others"])
    elif db_name=="user_dataDB":
        category=categorize(query,["personal_data",
                                  "goals",
                                  "preferences",
                                  "medical_constraints",
                                  "fitness_level",
                                  "workout_logs",
                                  "workout_plans",
                                  "meal_logs",
                                  "meal_plans"])
    elif db_name=="out of scope":
        return Command(goto="output_node",update={'answer':'The query is out of scope and irrelevant'}
                       )
    elif db_name=="Malicious request":
        return Command(goto="output_node",update={'answer':'Access Denied! Malicious Request Detected'})
    
    else:
        raise ValueError("Invalid database name returned by LLM")
    
    return Command(update={
        "database_name": db_name,
        "category": category
    },goto="rag_node")

def rag_agent_wrapper(state: ChatAgentState):
    answer,scores= rag_chat(state['query'],
                            state['category'],
                            state['user_name'],
                            state['database_name'])
    
    if answer=="lookout":
        return Command(goto="LookOutAgent",update={"answer":answer,"scores":scores})
    
    elif "sorry" in answer.lower().strip().split(' '):
        return Command(goto="output_node",update={"answer":answer,"scores":scores})
    else:
        return {
            "answer": answer,
            "scores": scores
        }

def validate_rag(state: ChatAgentState) -> ChatAgentState:
    if state['database_name']=='user_dataDB':
        return 'enough'
    prompt=f"""
-You are a validation agent.    
-You have provided an answer to the user's query using a RAG approach.
-Check if the answer is relevant and accurate based on the user's query or we need to fetch data from web search.
User Query: {state['query']}
Answer: {state['answer']}
scores: {state['scores']}
-make sure the scores must be greater than 0.8.
-If the answer is relevant and accurate and the scores are greater than 0.8, return "enough"
-If the answer is not relevant or accurate, return "look around"
-only return single word output no other words and no salutations.
"""
    response=llm.invoke(prompt)
    state_response=response.content.strip().lower()
    return state_response

def LookerAgent_wrapper(state: ChatAgentState):
    answer=looker(state['query'])
    
    return {"answer": answer}

def looker_output_structure_node(state: ChatAgentState):
    prompt=f"""
You are (Nutrition, Energy and Exercise Agent)NEXA AI, a fitness and diet related AI assistant.
you are very courteous and polite to users.
answer: {state['answer']}
query:{state['query']}
-add salutaions if required.
-rephraze only if required.
-dont change the meaning of the answer or add any new information.
-return answer in a concise and accurate according to the query
"""
    response=llm.invoke(prompt)
    final_ouput=response.content
    return {'final_output':final_ouput}


chat_graph=StateGraph(ChatAgentState)

chat_graph.add_node('query_node',query_node)
chat_graph.add_node('rag_node',rag_agent_wrapper)
chat_graph.add_node('LookOutAgent',LookerAgent_wrapper)
chat_graph.add_node('output_node',looker_output_structure_node)

chat_graph.add_edge(START,'query_node')
chat_graph.add_conditional_edges('rag_node',validate_rag,{
    'enough':'output_node',
    'look around': 'LookOutAgent'
})

chat_graph.add_edge('LookOutAgent','output_node')
chat_graph.add_edge('output_node',END)

ChatNexa=chat_graph.compile()




    
