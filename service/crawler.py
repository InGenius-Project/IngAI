import logging

import requests
from bs4 import BeautifulSoup
from requests import Response

import config
from middlewares import ExcpetionHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


class Crawler:
    def __init__(self) -> None:
        pass

    @ExcpetionHandler.handle_http_excpetion
    @staticmethod
    def check_company_exist(company_name) -> bool:
        api = config.get_gov_gcis_api(company_name)
        res = requests.get(api)
        if res.status_code != 200:
            logger.error(f"check_company_exist: cannot retrive response from api {api}")
            return False
        logger.info(f"check_company_exist: response {res.json()}")
        return len(res.json()) > 0

    @staticmethod
    def _get_anti_token(session: requests.Session) -> str:
        response = session.get(config.ACCOUNTING_FIRM_API)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find("input", {"name": "AntiToken"})
        return tag.get("value")

    @staticmethod
    def _get_result_list(session: requests.Session, search_api: str) -> str:
        response = session.get(search_api)
        soup = BeautifulSoup(response.content, "html.parser")
        result_list = soup.find_all("tr")
        return result_list

    @ExcpetionHandler.handle_http_excpetion
    def check_accounting_firm_exist(self, accounting_firm: str) -> bool:
        session = requests.Session()

        # Get AntiToken
        antitoken = self._get_anti_token(session)

        # Get search result
        search_api = config.get_accounting_firm_search_api(accounting_firm, antitoken)
        result_list = self._get_result_list(session, search_api)

        # Check is result trustable
        while result_list == []:
            # clear session
            session.close()
            antitoken = self._get_anti_token(session)
            search_api = config.get_accounting_firm_search_api(
                accounting_firm, antitoken
            )
            result_list = self._get_result_list(session, search_api)

        # Check is result exist
        is_exist = result_list[1].td.text == "1"
        return is_exist

    def get_industry_average_salary(self, industry: str) -> str:
        url = config.get_salary_api(industry)
        res: Response = self._session.get(url)
        if res.status_code != 200:
            logger.error(
                f"get_industry_average_salary: cannot retrive response from api {url}"
            )
            return "無法取得資料"
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.find("td").text
