from .LLM_Gateway import nexa_ai
from .database_utils import text_to_db
from langchain_community.retrievers import ArxivRetriever
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from tavily import TavilyClient
import streamlit as st
llm = nexa_ai()

def extract_keywords(query:str):
    prompt = f"""
    You are a websearch keyword extraction assistant.
    -Extract keywords from the following query: {query} for better web search results.
    -combine these keywords into a single string.
    -the string legnth should not exceed 100 words.
    -Provide restructred query only.no extra words, no salutations needed."""
    response = llm.invoke(prompt)
    return response.content



@tool
def get_papers(query: str):
    """If the user query needs research papers, use this tool to fetch relevant research papers from arXiv."""
    retriever = ArxivRetriever(
    load_max_docs=5,
    get_fulldoc=True
    )
    keywords=extract_keywords(query)
    docs = retriever.invoke(keywords)

    return docs



@tool
def web_search(query: str):
    """If the user query needs web search results, use this tool to fetch relevant results from the web."""
    keywords=extract_keywords(query)
    key=st.secrets["TAVILY"]
    client = TavilyClient(api_key=key)
    res = client.search(keywords, max_results=1)
    text_to_db(res["results"][0]['content'])
    return res["results"][0]['content']


import pdfplumber
def pdf_extracter(path: str):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text




