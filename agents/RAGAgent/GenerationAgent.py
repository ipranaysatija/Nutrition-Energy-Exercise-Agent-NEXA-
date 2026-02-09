from agents.RAGAgent.RAG_AgentState import AgentState
from tools.LLM_Gateway import nexa_ai
llm=nexa_ai()
def generation_agent(state: AgentState) -> AgentState:
    print("Generating answer...")
    query=state['rewrite_query']
    context=state['reranked_context']
    prompt = f"""
    You are a generation agent.
    task: Using the following context, generate a comprehensive answer to the query.
    Context: {context}
    Query: {query}
    -note that the provided context is ranked based on relevance to the query. so use the topmost relevant context more prominently in the answer.
    -only use the provided context to generate the answer.Dont add information on your own.
    -dont give answers that can be bad for the user, you can over right user preferences if needed.
    -Only return the final answer without any additional information or salutations."""
    response = llm.invoke(prompt)
    answer=response.content.strip()
    print("answer:",answer)
    return {"answer": answer}