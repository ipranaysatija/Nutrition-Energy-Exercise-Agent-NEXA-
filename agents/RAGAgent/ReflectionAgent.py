from agents.RAGAgent.RAG_AgentState import AgentState
from tools.LLM_Gateway import nexa_ai
import re
import json
llm=nexa_ai()
def reflection_agent(state: AgentState) -> AgentState:
    print("Reflecting on the answer...")
    answer=state['answer']
    context=state['retrieved_context']
    context_str="\n".join(context)
    prompt = f"""Evaluate the quality of the following answer based on:
                    1. relevance (is answer relevant to query?)
                    2. groundedness (is answer relevant to context?)
                    3. context_relevance (is context relevant to query?)
                    4. clarity (answer completely answered the query in a clear manner?)
                    5. justification (justify why you gave the respective scores)
    query:{state['query']}
    answer: {answer}
    context: {context_str}
    -Provide a score between 0 and 1, where 0.95 is excellent and 0.1 is poor.
    -Only return JSON without any additional information or salutations.
    -format: {{"relevance": float, 
                "groundedness": float, 
                "context_relevance": float, 
                "clarity": float
                "justification":str}}"""
    response = llm.invoke(prompt)
    match=re.search(r"\{.*\}",response.content,re.S)
    json_s=match.group(0) if match else ""
    score=json.loads(json_s)
    return {"scores": score}