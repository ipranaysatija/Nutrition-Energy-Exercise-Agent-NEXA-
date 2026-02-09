from langchain.tools import tool
from tools.LLM_Gateway import nexa_ai
def categorize(content: str, categories: list):
    """Categorize the given content into predefined categories."""
    prompt=f"""
    role: your are a categorizing agent.
    task: categorize the following content into one of the following categories: {', '.join(categories)}.
    content: {content}

    no salutations needed,
    output: return only the category name.
    """
    llm = nexa_ai()
    response = llm.invoke(prompt)
    return response.content
@tool
def daily_data_calc():
    """Calculate daily data statistics."""
    pass

@tool
def BMI_calc():
    """Calculate Body Mass Index (BMI)."""
    pass

