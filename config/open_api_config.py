OPENAI_PROTOCAL = "http://"
OPENAI_HOST = "api.openai.com"
OPENAI_API = OPENAI_PROTOCAL + OPENAI_HOST + "/v1/models"
OPENAI_MODEL = "gpt-4-turbo-preview"

CHAT_BOT_SYSTEM_LIMITATION_PROMPT = """是一個聊天機器人，並且只能回答實習有關的問題，其他一律回答我不知道你/妳在問甚麼\n"""
ANALYZATION_USER_PREFIX_PROMPT = "以提供的事實資料(事實資料絕對為真)以及常識為基礎, 提供150字左右的徵才文章詐騙分析報告給我:\n"
ANALYZATION_SYSTEM_PROMPT = "你是一個詐騙文章分析專家, 會根據所提供的事實分析文章內容\n"

RESUME_AREA_GENERATE_PREFIX_PROMPT = '依照 使用者的資訊 與 Title 來生成對應的 JSON 資料, 目標是要產生符合 Title 的讓使用者可以獲得更高機率的獲取機會的內容。\n需要滿足的輸出條件: """1. 只輸出 JSON 結果, 不要有多餘的話\n2.不要輸出空格\n"""'
RESUME_AREA_GENERATE_POSTFIX_PROMPT = '\nAreaTitle 包含但不限於: """- 簡介\n- 技能\n- 經驗\n- 聯絡資訊"""\n需輸出的 JSON 範例: """[{"AreaTitle": "自我簡介","Content": "[根據使用者的資料產生自我簡介的描述]"},{"AreaTitle": "經驗描述","Content": "[根據使用者的資料產生經驗的描述]"}]"""'

RESUME_AREA_GENERATE_BY_TITLE_PREFIX_PROMPT = '依照 使用者的資訊 與 Title 與提供的 AreaTitles 來生成對應的 JSON 資料。\n需要滿足的輸出條件: """1. 只輸出 JSON 結果, 不要有多餘的話\n2.不要輸出空格\n"""'
RESUME_AREA_GENERATE_BY_TITLE_POSTFIX_PROMPT = '\n需輸出的 JSON 範例: """[{"AreaTitle": "自我簡介","Content": "[根據使用者的資料產生自我簡介的描述]"},{"AreaTitle": "經驗描述","Content": "[根據使用者的資料產生經驗的描述]"}]"""'

RESUME_AREA_TITLE_GENERATE_PREFIX_PROMPT = '依照 使用者的資訊 與 Title 來生成對應的 JSON 資料, 產生 Resume 中會出現的 AreaTitle\n需要滿足的輸出條件: """1. 只輸出 JSON 結果, 不要有多餘的話\n2.不要輸出空格\n"""'
RESUME_AREA_TITLE_GENERATE_POSTFIX_PROMPT = '\n需輸出的 JSON ARRAY 範例: """[{"AreaTitle": "自我簡介"}, {"AreaTitle": "經驗描述"}]"""'

KEYWORD_EXTRACTION_PROMPT = '請對該以上文字做關鍵字分析, 我要你產生一個json輸出, 輸出範例: """{"keywords":["服務業","會計師"]}"""'

RECRUITMENT_AREA_GENERATE_PREFIX_PROMPT = '依照 公司的資訊 與 Title 來生成對應的 JSON 資料, 目標是要產生符合 Title 的讓應徵者可以對這個職缺感興趣。\n需要滿足的輸出條件: """1. 只輸出 JSON 結果, 不要有多餘的話\n2.不要輸出空格\n"""'
RECRUITMENT_AREA_GENERATE_POSTFIX_PROMPT = '\nAreaTitle 包含但不限於: """- 公司簡介\n- 需求技能\n- 需求經驗\n- 聯絡資訊"""\n需輸出的 JSON 範例: """[{"AreaTitle": "公司簡介","Content": "[根據公司的資料產生公司簡介的描述]"},{"AreaTitle": "技能需求","Content": "[產生可能的公司技能需求]"}]"""'

RECRUITMENT_AERA_GENERATE_BY_TITLE_PREFIX_PROMPT = '依照 公司的資訊 與 Title 與提供的 AreaTitles 來生成對應的 JSON 資料。目標是要產生符合 Title 的讓應徵者可以對這個職缺感興趣。\n需要滿足的輸出條件: """1. 只輸出 JSON 結果, 不要有多餘的話\n2.不要輸出空格\n"""'
RECRUITMENT_AREA_GENERATE_BY_TITLE_POSTFIX_PROMPT = '\n需輸出的 JSON 範例: """[{"AreaTitle": "公司簡介","Content": "[根據公司的資料產生公司簡介的描述]"},{"AreaTitle": "技能需求","Content": "[產生可能的公司技能需求]"}]"""'

RECRUITMENT_AREA_TITLE_GENERATE_PREFIX_PROMPT = '依照 公司的資訊 與 Title 來生成對應的 JSON 資料, 產生 職缺中 中會出現的 AreaTitle\n需要滿足的輸出條件: """1. 只輸出 JSON 結果, 不要有多餘的話\n2.不要輸出空格\n"""'
RECRUITMENT_AREA_TITLE_GENERATE_POSTFIX_PROMPT = '\n需輸出的 JSON ARRAY 範例: """[{"AreaTitle": "公司簡介"}, {"AreaTitle": "需求技能"}]"""'


def RESUME_AREA_GEN_SYS_PROMPT(area_num: int, title_only: bool, by_title: bool = False):
    if by_title:
        return (
            RESUME_AREA_GENERATE_BY_TITLE_PREFIX_PROMPT
            + RESUME_AREA_GENERATE_BY_TITLE_POSTFIX_PROMPT
        )
    if title_only:
        return (
            RESUME_AREA_TITLE_GENERATE_PREFIX_PROMPT
            + f"至少生成的 AreaTitle 數量: {area_num}\n"
            + RESUME_AREA_TITLE_GENERATE_POSTFIX_PROMPT
        )
    return (
        RESUME_AREA_GENERATE_PREFIX_PROMPT
        + f"至少生成的 AreaTitle 數量: {area_num}\n"
        + RESUME_AREA_GENERATE_POSTFIX_PROMPT
    )


def RECRUITMENT_AREA_GEN_SYS_PROMPT(
    area_num: int, title_only: bool, by_title: bool = False
):
    if by_title:
        return (
            RECRUITMENT_AERA_GENERATE_BY_TITLE_PREFIX_PROMPT
            + RECRUITMENT_AREA_GENERATE_BY_TITLE_POSTFIX_PROMPT
        )
    if title_only:
        return (
            RECRUITMENT_AREA_TITLE_GENERATE_PREFIX_PROMPT
            + f"至少生成的 AreaTitle 數量: {area_num}\n"
            + RECRUITMENT_AREA_TITLE_GENERATE_POSTFIX_PROMPT
        )
    return (
        RECRUITMENT_AREA_GENERATE_PREFIX_PROMPT
        + f"至少生成的 AreaTitle 數量: {area_num}\n"
        + RECRUITMENT_AREA_GENERATE_POSTFIX_PROMPT
    )
