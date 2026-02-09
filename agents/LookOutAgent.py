from tools.lookout_utils import get_papers, web_search, pdf_extracter
from langchain.agents import create_agent
from tools.LLM_Gateway import nexa_ai
from tools.database_utils import to_db
from tools.general_util import categorize
from langchain_core.documents import Document
from typing import List

def looker(query: str):
    looker=create_agent(
        model=nexa_ai(),
        tools=[get_papers, web_search],
        system_prompt="""You are a Research agent,
        when you recieve a query, you fetch data from web_search and get_papers tools. use model only if required"""
    )
    response=looker.invoke( {"messages": [{"role": "user", "content": query}]})
    return response['messages'][-1].content

def extracter(path: str,context):
    """Extract content from various document formats. 
    To be used incase of media uploads"""
    source=path.split("/")[-1]
    docs:List[Document]=[]
    text=pdf_extracter(path)
    for section in text.split('/sec'):
        lines=section.strip().splitlines()
        for line in lines:
            doc=Document(page_content=line, metadata={"source": source, "category": context,"section":lines[0]})
            docs.append(doc)
    to_db(docs, database_name="agentKB")
    return
    


