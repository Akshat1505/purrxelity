from datetime import date
from langchain.tools import tool

@tool
def get_curr_date():
    """
    Tool to get the current datetime in case needed
    Args: None
    Returns: Current Date in the format (%Y%m%d e.g. 20250712 for 12th July 2025)
    """
    current_date=date.today().strftime("%Y%m%d") #User selected dates
    return current_date

if __name__=="__main__":
    print(get_curr_date.invoke({}))
