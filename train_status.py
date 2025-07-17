import json,os,requests
from datetime import date
from langchain_core.tools import tool

@tool
def search_train(source:str,destination:str):
    """
    Tool to get ticket availability in a train between source and destination station for current date
    Args:
    source(str): The source station code (e.g. "BE").
    destination(str): The destination station code (e.g. "NDLS").
    Returns:
    A JSON object containing information about train availability, including train name, number and class availability with fares
    abbreviation SL-Sleeper, 3A-Third AC, 2A-Second AC, 1A-First AC 
    """
    departure_date=date.today().strftime("%Y%m%d")
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

    # print("Status -> ",response.status_code)

    if response.status_code==200:
        train_data=response.json()["body"]["trains"]
        if not train_data: return "No trains found for the given date"
        formatted_result={}
        for train in train_data:
            curr_train=train["trainName"]+"-"+train["trainNumber"]
            coach_class_stor_temp=[]
            for coach_class in train["availability"]:
                coach_class_stor_temp.append({
                    "code":coach_class.get("code"),
                    "fare":int(coach_class.get("fare")), #can explode use try except
                    "status_shortform":coach_class.get("status_shortform")
                })
            formatted_result[curr_train]=coach_class_stor_temp
        return formatted_result

    else:
        raise Exception(f"Failed with {response.status_code}")
#
# for train in search_train.invoke({"source":"BE","destination":"NDLS"})["body"]["trains"]:
#     print(f"Train Name {train["trainName"]} Train Number {train["trainNumber"]}")
#     for coach_class in train["availability"]:
#         print(f"Class {coach_class["code"]} Fare {coach_class["fare"]} Aval {coach_class["status_shortform"]}") #fare not aval tatkal
if __name__=="main":
    print(search_train.invoke({"source":"BE","destination":"NDLS"}))
