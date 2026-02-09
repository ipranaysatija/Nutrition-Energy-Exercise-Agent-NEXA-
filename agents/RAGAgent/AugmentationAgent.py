from agents.RAGAgent.RAG_AgentState import AgentState
from tools.LLM_Gateway import nexa_ai
llm=nexa_ai()
def augmentation_agent(state: AgentState) -> AgentState:
    print("Re-ranking context...")
    query=state['rewrite_query']
    context=state['retrieved_context']
    reranked_context=""
    temp={}
    for idx, chunk in enumerate(context,start=1):
        prompt = f"""score the following chunk based on its relevance to the query.
        Provide a relevance score between 0 and 1, where 1 is highly relevant and 0 is not relevant at all.
        chunk: {chunk}
        query: {query}
        -Only return the score without any additional information or salutations."""
        response = llm.invoke(prompt)
        score=float(response.content.strip())
        temp[chunk]=score
    for index,chunk in enumerate(sorted(temp, key=temp.get, reverse=True),start=1):
        reranked_context+=f"\n Rank {index}: {chunk}"

    compress_prompt=f"""
                        You are a context compression agent
                        from context you extract  chunks from each rank that are relevant to the query.
                        query:{query}
                        context:{reranked_context}
                        -keep maximum chunks preserved
                        -preserve the ranks of the context in chunks
                        -return only retrieved relevant chunks alnog with their rank and no extra words or salutations.
                        """
    res=llm.invoke(compress_prompt)
    compressed_context=res.content


    summarize_prompt=f"""
                                    You are a context summarizing agent.
                                    -summarize each rank ofthe given context keeping all the relevant information required to answer query
                                    -preserve the ranks of the context provided

                                    context:{compressed_context}
                                    query:{query}
                                    -only return summarized chunk of eachrank along with rank without any extra words or salutations.
"""
    res=llm.invoke(summarize_prompt)
    final_context=res.content
    print("-------------------------------------------")
    print("reranked")
    print(reranked_context)
    print("-------------------------------------------")
    print("Compressed")
    print(compressed_context)
    print("-------------------------------------------")
    print("final")
    print(final_context)
    print("-------------------------------------------")
    return {"reranked_context": final_context}