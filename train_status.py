import json,os,requests
from datetime import date

current_date=date.today()
fi_date=str(current_date).replace("-","")


def search_train(source:str,destination:str):
    departure_date=date.today().strftime("%Y%m%d")
    url = (
        "https://travel.paytm.com/api/trains/v5/search?"
        f"departureDate={departure_date}"
        f"&destination={destination}"
        f"&dimension114=direct-home"
        f"&isAscOfferEligible=false"
        f"&isH5=true"
        f"&is_new_user=false"
        f"&quota=GN"
        f"&show_empty=true"
        f"&source={source}"
        f"&user_type=active"
        f"&client=web"
        f"&deviceIdentifier=Mozilla%20Firefox-140.0"
    )
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }

    response=requests.get(url,headers=headers)

    print("Status -> ",response.status_code)

    if response.status_code==200:
        return response.json()
    else:
        raise Exception(f"Failed with {response.status_code}")

for train in search_train("BE","NDLS")["body"]["trains"]:
    print(f"Train Name {train["trainName"]} Train Number {train["trainNumber"]}")
    for coach_class in train["availability"]:
        print(f"Class {coach_class["code"]} Fare {coach_class["fare"]} Aval {coach_class["status_shortform"]}") #fare not aval tatkal
