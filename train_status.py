import json,os,requests
from datetime import date
from langchain_core.tools import tool

@tool
def search_train(source:str,destination:str,departure_date:str):
    """
    Tool to get ticket availability in a train between source and destination station for current date
    Args:
    source(str): The source station code (e.g. "BE").
    destination(str): The destination station code (e.g. "NDLS").
    departure_date(str): The departure_date in the YYYYMMDD format (e.g. "20250815")
    Returns:
    A JSON object containing information about train availability, including train name, number and class availability with fares
    abbreviation SL-Sleeper, 3A-Third AC, 2A-Second AC, 1A-First AC. If fare for any class is shown as 0 take it as infinite and don't mention it to the user.
    """
    # departure_date=date.today().strftime("%Y%m%d")
    # print(departure_date)
    url = (
        "https://travel.paytm.com/api/trains/v5/search?"
        f"departureDate={departure_date}"
        f"&destination={destination.capitalize()}"
        f"&dimension114=direct-home"
        f"&isAscOfferEligible=false"
        f"&isH5=true"
        f"&is_new_user=false"
        f"&quota=GN"
        f"&show_empty=true"
        f"&source={source.capitalize()}"
        f"&user_type=active"
        f"&client=web"
        f"&deviceIdentifier=Mozilla%20Firefox-140.0"
    )
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }

    response=requests.get(url,headers=headers)

    if response.status_code==200:
        train_data=response.json()["body"]["trains"]
        if not train_data: return "No trains found for the given date"
        formatted_result={}
        for train in train_data:
            curr_train=train["trainName"]+"-"+train["trainNumber"]
            coach_class_stor_temp=[]
            for coach_class in train["availability"]:
                fare_value=coach_class.get("fare")
                try:
                    fare_int=int(fare_value)
                except (ValueError,TypeError):
                    fare_int=0
                coach_class_stor_temp.append({
                    "code":coach_class.get("code"),
                    "fare":fare_int, #can explode use try except
                    "status_shortform":coach_class.get("status_shortform")
                })
            formatted_result[curr_train]=coach_class_stor_temp
        return json.dumps(formatted_result,indent=4)

    else:
        raise Exception(f"Failed with {response.status_code}")

if __name__=="__main__":
    print(search_train.invoke({"source":"BE","destination":"NDLS","departure_date":"20250820"}))
