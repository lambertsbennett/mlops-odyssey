import requests
from datetime import datetime, timedelta
import json

# OpenAQ base URL.
BASE_URL = "https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com"


def healthy_connection():
    r = requests.get(f"{BASE_URL}/ping")
    if r.status_code == 200:
        return True
    else:
        return False


# Get historical data for Vienna 
def get_historical_data(start, end, data_category="pm25", all=False, limit=10000):
    if all:
        params = {"country":"AT", "city": "Wien", "date_from": start, "date_to": end, "limit": limit}
        r = requests.get(f"{BASE_URL}/v2/measurements", params=params)
        response_data = r.json()["results"]

    else:
        params = {"country":"AT", "city": "Wien", "parameter": data_category, "date_from": start, "date_to": end, "limit": limit}
        r = requests.get(f"{BASE_URL}/v2/measurements", params=params)
        response_data = r.json()["results"]
    
    return response_data


def main():

    current_date = datetime.now()
    previous_date = current_date - timedelta(days=1)
    
    if healthy_connection():
        r = get_historical_data(previous_date.date(), current_date.date(), all=True, limit=10000)
    else:
        raise Exception("Could not connect to OpenAQ API.")

    with open("/results.json", "w") as f:
        json.dump(r, f)

if __name__ == '__main__':
    main()