from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List
from tools.general_util import categorize
from tools.LLM_Gateway import embedding_model
from tools.database_utils import get_criticality,get_policy,to_db

def user_data_loger(content: dict, user_name:str):
        data_type = categorize(str(content), ["personal_data",
                                            "goals",
                                            "preferences",
                                            "medical_constraints",
                                            "fitness_level",
                                            "workout_logs",
                                            "workout_plans",
                                            "meal_logs",
                                            "meal_plans"])
            
        criticality=get_criticality(str(content))
        
        doc=Document(page_content=str(content), metadata={
            'user_name':user_name,
            'coach': content['coach_id'],
            'data_type': data_type,
            'date': content['created_at'],
            'criticality': criticality ,
            'policy': get_policy(str(content),criticality)
            })
        to_db([doc],database_name="user_dataDB")

        return "data pushed to db"