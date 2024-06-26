from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from test_article import TEST_ARTICLE


class MessageModel(BaseModel):
    role: str
    content: str


class FactsModel(BaseModel):
    work_hour: str = "在台灣, 勞工正常工作時間, 每日不得超過8小時, 每週不得超過40小時"
    base_salary: str = "在台灣, 現行基本工資為月薪新臺幣27470元、時薪新臺幣183元"
    industry_avarage_salary: str = "未知"
    is_company_record_gorvernment: bool = False

    def generate_text(self):
        return f'\n事實: """\n工作時間: {self.work_hour}\n基本工資: {self.base_salary}\n產業平均薪資: {self.industry_avarage_salary}\n公司已登記於政府資料庫: {"是" if self.is_company_record_gorvernment else "否"}\n"""\n'


class Industry(str, Enum):
    SoftwareEngineering: str = "軟體工程"
    FinancialProfessionals: str = "金融"
    Accounting: str = "會計服務業"
    Insurance: str = "保險"
    Industrial: str = "工業"


class WorkType(str, Enum):
    FullTime: str = "全職"
    PartTime: str = "兼職"
    Intern: str = "實習"


class Article(BaseModel):
    CompanyName: str
    Facts: Optional[FactsModel] = None
    # workType: WorkType
    Content: str
    # Industry: Industry

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "鼎榮會計師事務所",
                "workType": "兼職",
                "content": TEST_ARTICLE,
                "industry": "會計服務業",
            },
        }
    }

    def generate_text(self):
        return f'{self.Facts.generate_text()}\n文章: """\n{self.Content}\n"""'
