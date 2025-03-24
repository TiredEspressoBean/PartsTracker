import requests
from django.conf import settings

API_KEY = settings.HUBSPOT_API_KEY

HUBSPOT_API_BASE_URL = 'https://api.hubapi.com/crm/v3'
HEADERS = {
    "Authorization": "Bearer " + settings.HUBSPOT_API_KEY,
    "Content-Type": "application/json",
}

def get_all_deals():
    all_deals_data = []
    params = {"limit": 100, "archived": "false"}

    while True:
        deal_url = HUBSPOT_API_BASE_URL + "/objects/deals"
        response = requests.get(deal_url, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}: {response.text}")
            break

        data = response.json()
        all_deals_data.extend(data.get("results", []))

        next_page_info = data.get("paging", {}).get("next")
        if not next_page_info:
            break
        params["after"] = next_page_info["after"]

    return all_deals_data


def get_companies_from_deal_id(deal_id):
    companies_data = []
    for deal in deal_id:
        deal_url = HUBSPOT_API_BASE_URL + "/associations/Deals/Companies/batch/read"
        response = requests.get(deal_url, headers=HEADERS, params={"inputs": [{"id": deal}]})
<<<<<<< HEAD
        x=0
=======
~        x=0
>>>>>>> 53a4b77 (B)

def get_contacts_from_deal_id(deal_id):
    contacts_data = []