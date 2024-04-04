import os
from typing import Generator, Iterable, List

from dotenv import load_dotenv
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
from model import Article, MessageModel
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
        self, messages: Iterable[MessageModel], stream=False
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        parsed_messages = self.convert_to_chat_completion(messages)
        response_stream = self._client.chat.completions.create(
            model=self.__model__,
            messages=parsed_messages,
            stream=stream,
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
        if "會計師事務所" in article.company_name:
            article.company_name = article.company_name.replace("會計師事務所", "")
            article.facts.is_company_record_gorvernment = (
                crawler.check_accounting_firm_exist(article.company_name)
            )
        else:
            article.facts.is_company_record_gorvernment = Crawler.check_company_exist(
                article.company_name
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
