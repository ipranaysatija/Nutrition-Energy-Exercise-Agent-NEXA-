from  agents.RAGAgent.RAG_AgentState import AgentState
from tools.LLM_Gateway import nexa_ai
from langgraph.types import Command
from langgraph.graph import END
llm=nexa_ai()

def rewrite_query(state: AgentState) -> AgentState:
    print("Rewriting query...")
    user_query=state['query']
    prompt = f"""
    You are a query re-writting agent.
    -Task 1: break user_query into smaller keywords for better retreival from database
    -Task2: combine the keywords to get relevant data chunks and return the rewritten query
    
    user_query:{user_query}
    -Only return the rewritten query without any additional information or salutations."""
    response = llm.invoke(prompt)
    rewritten_query=response.content
    return {"rewrite_query": rewritten_query}

def knowledge_base_retriever(query,db,category):
    knowledge_base_retriever=db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5,"filter":{"category":category}}
)
    retrieved_context=knowledge_base_retriever.invoke(query)
    return [doc.page_content for doc in retrieved_context]

def user_data_retriever(query,db,user_name,category):
    user_data_retriever=db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5,"filter":{"user_name":user_name}}
)
    retrieved_context=user_data_retriever.invoke(query)
    return [doc.page_content for doc in retrieved_context]

def retrieval_agent(state: AgentState) -> AgentState:
    print("Retrieving context...")
    query=state['rewrite_query']
    category=state['category']
    db=state['db']
    user_name=state['user_name']
    database_name=state['database_name']

    if database_name=="agentKB":
        retrieved_context=knowledge_base_retriever(query,db,category)
        if retrieved_context:
            return Command(update={"retrieved_context":retrieved_context},goto="augmentation_agent")
        else:
            return Command(goto=END,update={'answer': 'lookout'})
        
    elif database_name=="user_dataDB":
        retrieved_context=user_data_retriever(query,db,user_name,category)
        if retrieved_context:
            return Command(update={"retrieved_context":retrieved_context},goto="augmentation_agent")
        else:
            return Command(goto=END, update={'answer': 'sorry couldnt find what you were looking for'})
    else:
        raise ValueError("Bad DB address!")

    
    