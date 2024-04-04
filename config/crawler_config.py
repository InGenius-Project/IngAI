ACCOUNTING_FIRM_API = "https://www.roccpa.org.tw/member_search/"


def get_accounting_firm_search_api(accounting_firm: str, antitoken: str):
    return (
        f"{ACCOUNTING_FIRM_API}?AntiToken={antitoken}&fields=2&keys={accounting_firm}"
    )


def get_gov_gcis_api(company_name: str):
    return f"https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=json&$filter=Company_Name like {company_name} and Company_Status eq 01&$skip=0&$top=50"
