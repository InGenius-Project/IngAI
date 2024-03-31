import logging

import requests
from bs4 import BeautifulSoup
from requests import Response, Session

import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def check_accoutant_exist(keyword):

    url = "https://www.roccpa.org.tw/member_search/"

    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"

    headers = {"User-Agent": userAgent}


class Crawler:
    def __init__(self) -> None:
        self._session: Session = requests.Session()

    @staticmethod
    def check_company_exist(company_name) -> bool:
        api = config.get_gov_gcis_api(company_name)
        res = requests.get(api)
        if res.status_code != 200:
            logger.error(f"check_company_exist: cannot retrive response from api {api}")
            return False
        logger.info(f"check_company_exist: response {res.json()}")
        return len(res.json()) > 0

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
