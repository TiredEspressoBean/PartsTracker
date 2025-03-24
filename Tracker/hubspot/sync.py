from Tracker.hubspot.api import get_all_deals, get_contacts_from_deal_id, get_companies_from_deal_id
# from Tracker.models import Deal, Company, User
def sync_all_deals():
    deals_data = get_all_deals()
    if not deals_data:
        return "Failed to retrieve all deals from HubSpot."

    for deal in deals_data:
        try:
            deal_name = deal['properties']['dealname']
            deal_stage_id = deal['properties']['dealstage']
            last_modified_date = deal['properties']['hs_lastmodifieddate']
            created_date = deal['properties']['createdate']
            close_date = deal['properties']['closedate']
            deal_id = deal['id']
            deal_pipeline_id = deal['properties']['pipeline']

            # contact = get_contacts_from_deal_id([deal_id])
            companies = get_companies_from_deal_id([deal_id])


        except:
            return "Failed to retrieve deals from HubSpot."

