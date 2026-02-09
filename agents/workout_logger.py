from tools.LLM_Gateway import nexa_ai
import json
import re
from datetime import datetime
llm=nexa_ai()
def get_workout_details(workout_item: str, duration_minutes: float,) -> dict:
    prompt=f"""
    you are a workout details calculator.
    given a workout_item and duration, return its details.
    workout_item: {workout_item}
    duration: {duration_minutes} minutes
    -Provide the response in JSON format with keys: calories_burned, intensity, description.
    -no additional text outside the JSON. No salutations
    """
    response=llm.invoke(prompt)
    match=re.search(r"\{.*\}",response.content,re.S)
    json_s=match.group(0) if match else ""
    macros=json.loads(json_s)
    return {
        "workout_item": workout_item,
        "duration_minutes": duration_minutes,
        "workout_details": macros,
        "date_time":datetime.now().isoformat()
    }

