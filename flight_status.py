import json,os,requests
from datetime import date
import urllib.parse
from langchain.tools import tool

@tool
def search_train(source:str,destination:str,seating_class:str="E"):
    """
    Tool to get ticket availability in a train between source and destination station for current date
    Args:
    source(str): The source station code (e.g. "BE").
    destination(str): The destination station code (e.g. "NDLS").
    Returns:
    A JSON object containing information about train availability, including train name, number and class availability with fares
    abbreviation SL-Sleeper, 3A-Third AC, 2A-Second AC, 1A-First AC 
    """
    departure_date=date.today().strftime("%Y%m%d") #User selected dates
    params = {
        "origin": source,
        "destination": destination,
        "accept": "combination",
        "adults": "1",
        "children": "0",
        "infants": "0",
        "class": seating_class,
        "isH5": "true",
        "enable": '{"handBaggageFare":true,"paxWiseConvFee":true,"minirules":true}',
        "client": "web",
        "departureDate": "20250721",
        "userType": "discount",
        "cohort": "disc005",
        "productFlow": "nu_slasher",
        "user_id": "1434109935",
        "application_platform": "dweb",
    }    
    url = "https://travel.paytm.com/api/flights/v3/search?" + urllib.parse.urlencode(params)
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }
    response=requests.get(url,headers=headers)
    print(response.json())


if __name__=="__main__":
    search_train.invoke({"source":"DEL","destination":"PAR","seating_class":"P"})


