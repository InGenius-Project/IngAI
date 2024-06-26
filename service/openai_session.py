import json
import os
from typing import Any, Generator, Iterable, List

from dotenv import load_dotenv
from icecream import ic
from openai import Client, OpenAI
from openai._streaming import Stream
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion_message_param import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

import config
from model import AreaGenInfo, AreaGenType, Article, MessageModel
from service import Crawler

# load env file
load_dotenv()


class OpenAISession:
    def __init__(self):
        self.__TOKEN__ = os.getenv("OPENAI_API_KEY")
        self.__ORG_ID__ = os.getenv("OPENAI_ORG_ID")
        self.__OPENAI_API__ = config.OPENAI_API
        self.__model__ = config.OPENAI_MODEL
        if self.__TOKEN__ is None or self.__ORG_ID__ is None:
            raise Exception("OpenAI API Key or ORG ID not found")

        # Create OpenAI client
        self._client: Client = OpenAI(
            api_key=self.__TOKEN__,
            organization=self.__ORG_ID__,
        )

    def _post(
        self,
        messages: Iterable[MessageModel],
        stream=False,
        response_format="text",
        temperature=0.7,
        max_tokens=1500,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        parsed_messages = self.convert_to_chat_completion(messages)
        response_stream = self._client.chat.completions.create(
            model=self.__model__,
            messages=parsed_messages,
            stream=stream,
            response_format={"type": response_format},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response_stream

    @staticmethod
    def _read_stream(
        response_stream: Stream[ChatCompletionChunk],
    ) -> Generator[str, None, None]:
        for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    @staticmethod
    def _set_article_facts(article: Article) -> None:
        crawler = Crawler()
        # Check if the company is registered in the government database
        if "會計師事務所" in article.CompanyName:
            article.CompanyName = article.CompanyName.replace("會計師事務所", "")
            article.Facts.is_company_record_gorvernment = (
                crawler.check_accounting_firm_exist(article.CompanyName)
            )
        else:
            article.Facts.is_company_record_gorvernment = Crawler.check_company_exist(
                article.CompanyName
            )

    def chat(self, message: MessageModel, stream=True) -> Generator[str, None, None]:
        messages = [
            MessageModel(
                role="system", content=config.CHAT_BOT_SYSTEM_LIMITATION_PROMPT
            ),
            message,
        ]
        response_stream = self._post(messages, stream)
        return self._read_stream(response_stream)

    def extraction(self, content: str) -> List[str]:
        all_content = f'"""{content}"""\n' + config.KEYWORD_EXTRACTION_PROMPT
        response = self._post(
            [
                MessageModel(role="user", content=all_content),
            ],
            response_format="json_object",
            stream=False,
        )
        return json.loads(response.choices[0].message.content).get("keywords")

    def analyze(self, article: Article) -> str:
        self._set_article_facts(article)
        # Generate the text from the article
        user_text = config.ANALYZATION_USER_PREFIX_PROMPT + article.generate_text()

        response = self._post(
            [
                MessageModel(role="system", content=config.ANALYZATION_SYSTEM_PROMPT),
                MessageModel(role="user", content=user_text),
            ],
            stream=False,
        )
        return response.choices[0].message.content

    def generate_area(
        self,
        user_info: AreaGenInfo,
    ) -> str:
        if user_info.Type == AreaGenType.Resume:
            user_text = "使用者資料: \n" + f'"""{user_info.to_string()}"""'
        else:
            user_text = "公司資料: \n" + f'"""{user_info.to_string()}"""'

        match user_info.Type:
            case AreaGenType.Resume:
                system_prompt = config.RESUME_AREA_GEN_SYS_PROMPT(
                    user_info.AreaNum, user_info.TitleOnly
                )
            case AreaGenType.Recruitment:
                system_prompt = config.RECRUITMENT_AREA_GEN_SYS_PROMPT(
                    user_info.AreaNum, user_info.TitleOnly
                )

        ic("Request: ", user_text, "\n\n\n")

        messages = [
            MessageModel(
                role="system",
                content=system_prompt,
            ),
            MessageModel(role="user", content=user_text),
        ]

        response_stream = self._post(
            messages,
            stream=True,
            response_format="text",
            temperature=0.7,
            max_tokens=1500,
        )
        response = ""
        for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content

        json_object = json.loads(response)
        return json_object

    def generate_area_by_title(
        self, user_info: AreaGenInfo, area_titles: List[str]
    ) -> Any:
        if user_info.Type == AreaGenType.Resume:
            user_text = (
                "使用者資料: \n"
                + f'"""{user_info.to_string()}\nAreaTitles: {", ".join(area_titles)}\n"""'
            )
        else:
            user_text = (
                "公司資料: \n"
                + f'"""{user_info.to_string()}\nAreaTitles: {", ".join(area_titles)}\n"""'
            )

        match user_info.Type:
            case AreaGenType.Resume:
                system_prompt = config.RESUME_AREA_GEN_SYS_PROMPT(
                    user_info.AreaNum, user_info.TitleOnly
                )
            case AreaGenType.Recruitment:
                system_prompt = config.RECRUITMENT_AREA_GEN_SYS_PROMPT(
                    user_info.AreaNum, user_info.TitleOnly, True
                )

        ic("Request: ", user_text, "\n\n\n")

        response_stream = self._post(
            [
                MessageModel(
                    role="system",
                    content=system_prompt,
                ),
                MessageModel(role="user", content=user_text),
            ],
            stream=True,
            response_format="text",
            temperature=0.7,
            max_tokens=1500,
        )
        response = ""
        for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")

        print("\n\n")

        json_object = json.loads(response)
        return json_object

    def convert_to_chat_completion(
        self,
        messages: Iterable[MessageModel],
    ) -> Iterable[ChatCompletionMessageParam]:
        chat_completion_messages = []
        for message in messages:
            chat_completion_message = None
            if message.role == "system":
                chat_completion_message = ChatCompletionSystemMessageParam(
                    role="system", content=message.content
                )
            elif message.role == "user":
                chat_completion_message = ChatCompletionUserMessageParam(
                    role="user",
                    content=message.content,
                )
            if chat_completion_message is not None:
                chat_completion_messages.append(chat_completion_message)
        return chat_completion_messages
