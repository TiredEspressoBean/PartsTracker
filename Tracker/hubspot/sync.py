from Tracker.hubspot.api import get_all_deals, get_contacts_from_deal_id, get_company_ids_from_deal_id, extract_ids, get_company_info_from_company_ids, get_contact_info_from_contact_ids
from Tracker.models import Deal


# from Tracker.models import Deal, Company, User


def sync_all_deals():
    deals_data = get_all_deals()
    if not deals_data:
        return "Failed to retrieve all deals from HubSpot."

    deal_id_list = []
    deal_ids = {}
    for deal in deals_data:
        deal_ids[deal['id']] = {}
        deal_id_list.append(deal['id'])

    deal_ids_to_contacts_ids = get_contacts_from_deal_id(deal_id_list)
    deal_ids_to_companies_ids = get_company_ids_from_deal_id(deal_id_list)

    contact_ids = extract_ids(deal_ids_to_contacts_ids)
    company_ids = extract_ids(deal_ids_to_companies_ids)

    contact_dictionary = get_contact_info_from_contact_ids(contact_ids)
    company_dictionary = get_company_info_from_company_ids(company_ids)

    for deal in deals_data:
        obj, created = Deal.objects.update_or_create(

        )

