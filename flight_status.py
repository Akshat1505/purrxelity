import json,os,requests
# from datetime import date
import re
from typing import Annotated,Literal
import urllib.parse
from langchain.tools import tool


def duration_to_minutes(duration:str):
    parts=duration.replace('h',' ').replace('m','').split()
    hours=int(parts[0]) if len(parts) > 0 else 0
    minutes=int(parts[1]) if len(parts) > 1 else 0 
    return hours*60+minutes
@tool
def search_flight(source:str,destination:str,date:str,seating_class:str="E",sort:str="Price",adult:int=1,children:int=0):
    """
    Tool to get ticket availability in a flight between source and destination airport for current date
    Args:
    source(str): The source airport code (e.g. "JFK").
    destination(str): The destination station code (e.g. "CDG").
    date(string): 
    seating_class(str): User preference seating class defaulted to "E" (economy), "P" (premium economy), "B" (business). Defaults to "E" (economy)
    sort(str)(optional): Sorting airlines whether on price or time (e.g. "price" "duration"). Defaults to "price"
    Returns:
    adult(int): Number of Adults travelling. Defaults to 1.
    children(int)(optional): Number of Children travelling. Defaults to 0.
    A JSON object containing information about flight availability, including airline name, number and duration with fares and hops
    """
    # departure_date=date.today().strftime("%Y%m%d") #User selected dates
    params = {
        "origin": source,
        "destination": destination,
        "accept": "combination",
        "adults": adult,
        "children": children,
        "infants": "0",
        "class": seating_class,
        "isH5": "true",
        "enable": '{"handBaggageFare":true,"paxWiseConvFee":true,"minirules":true}',
        "client": "web",
        "departureDate": date,
        "userType": "discount",
        "cohort": "disc005",
        "productFlow": "nu_slasher",
        "user_id": "1",
        "application_platform": "dweb",
    }    
    url = "https://travel.paytm.com/api/flights/v3/search?" + urllib.parse.urlencode(params)
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }
    #787. Cheapest Flights Within K Stops
    response=requests.get(url,headers=headers)
    response_json=response.json()

    if response.status_code==200:
        flight_data=response_json["body"]["onwardflights"]["flights"]

        if not flight_data:
            return "No flights available for the current date"
        formatted_result={}

        for flight in flight_data:
            airline=flight["airline"]+"-"+flight["hops"][0]["flightNumber"]
            flight_information={
                # "airline":flight["airline"],
                "duration":flight["duration"],
                "hops":len(flight["hops"])-1,
                "price":flight["price"][0]["price"]
            }
            formatted_result[airline]=flight_information

        price_sorted=dict(sorted(formatted_result.items(),key=lambda item:item[1]["price"])[:10])
        duration_sorted=dict(sorted(formatted_result.items(),key=lambda item:duration_to_minutes(item[1]["duration"]))[:10])

        if sort.lower().strip()=="price":
            return json.dumps(price_sorted,indent=4)
        return json.dumps(duration_sorted,indent=4)
    else:
        raise Exception(f"Failed with {response.status_code}")

if __name__=="__main__":
    print(search_flight.invoke({"source":"DEL","destination":"HND","seating_class":"B","sort":"PriCe"}))


