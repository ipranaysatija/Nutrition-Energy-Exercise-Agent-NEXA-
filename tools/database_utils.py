from tools.general_util import categorize
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Optional
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tools.LLM_Gateway import embedding_model,nexa_ai
from datetime import date
def get_criticality(content: str):
    if ['allergy', 'health condition', 'diagnosis','health problem'] in content.strip().split(" "):
        return 'critical'
    else: 
        return 'Normal'
    
def get_policy(content: str, criticality: str):
    if ['risk', 'fatal', 'dangerous'] in content.strip().split(" ") and criticality=="critical":
        return "Removal"
    
    elif ['risk', 'fatal', 'dangerous'] in content.strip().split(" "):
        return "human review required"
    
    else:
        return "Acceptance"

def to_db(docs: List[Document], database_name: str):
    spliter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=['\n\n','\n','.',' ']
    )
    chunked_docs=spliter.split_documents(docs)

    index_file = os.path.join(f"{database_name}/", "index.faiss")
    if os.path.exists(index_file):
        db=FAISS.load_local(
            folder_path=f"{database_name}/",
            embeddings=embedding_model(),
            allow_dangerous_deserialization=True)
        db.add_documents(chunked_docs)
    else:
        print(chunked_docs)
        db=FAISS.from_documents(chunked_docs,embedding=embedding_model())
    db.save_local(folder_path=f"{database_name}/")

    return


def text_to_db(content: str, database_name: str = "agentKB", user_name: str="anonymous", coach_id: str="default"):
    """Function to store content in a database. Placeholder for actual DB implementation."""
    docs: List[Document] = []
    if database_name == "agentKB":
        category = categorize(content, ["food_items","workouts","fat_reduction","others"])
        doc=Document(page_content=content, metadata={"source": "web search", "category": category,"section":"one"})


    elif database_name == "user_dataDB":
        data_type = categorize(content, ["personal_data",
                                        "goals",
                                        "preferences",
                                        "medical_constraints",
                                        "fitness_level",
                                        "workout_logs",
                                        "workout_plans",
                                        "meal_logs",
                                        "meal_plans"])
        
        criticality=get_criticality(content)
        
        doc=Document(page_content=content, metadata={
            'user_name':user_name,
            'coach': coach_id,
            'data_type': data_type,
            'date': date.today().isoformat(),
            'criticality': criticality ,
            'policy': get_policy(content,criticality)
            })
        

    elif database_name == "system_logsDB":
        category = categorize(content, ["diet_plan","workout_plan","others"])

    docs.append(doc)
    to_db(docs,database_name=database_name)



        
