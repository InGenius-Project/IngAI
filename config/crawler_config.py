def get_gov_gcis_api(company_name: str):
    GOV_GCIS_API = f"https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=json&$filter=Company_Name like {company_name} and Company_Status eq 01&$skip=0&$top=50"
    return GOV_GCIS_API
