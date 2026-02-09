from tools.LLM_Gateway import nexa_ai
import json
import re
from datetime import datetime
llm=nexa_ai()
def get_macronutrient_breakdown(food_item: str, quantity: float,) -> dict:
    prompt=f"""
    you are a macronutrient calculator.
    given a food_item and quantity, return its macronutrient breakdown in grams (protein, fat, carbohydrates) and total calories.
    food_item: {food_item}
    quantity: {quantity} grams
    -Provide the response in JSON format with keys: protein, fat, carbohydrates, calories.
    -no additional text outside the JSON. No salutations
    """
    response=llm.invoke(prompt)
    match=re.search(r"\{.*\}",response.content,re.S)
    json_s=match.group(0) if match else ""
    macros=json.loads(json_s)
    return {
        "food_item": food_item,
        "quantity": quantity,
        "macronutrients": macros,
        "date_time":datetime.now().isoformat()
    }

