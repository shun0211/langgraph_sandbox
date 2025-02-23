from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models.interview import Interview
from models.evaluation import EvaluationResult


class InformationEvaluator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.with_structured_output(EvaluationResult)

    def run(self, user_request: str, interviews: list[Interview]) -> EvaluationResult:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは包括的な要件文書を作成するための情報の十分製を評価する専門家です。",
                ),
                (
                    "human",
                    "以下のユーザーリクエストとインタビュー結果に基づいて、包括的な要件定義書を作成するのに十分な情報が集まったかどうかを判断してください。\n\n"
                    "ユーザーリクエスト：{user_request}\n"
                    "インタビュー結果：{interview_results}",
                ),
            ]
        )

        chain = prompt | self.llm

        return chain.invoke(
            {
                "user_request": user_request,
                "interview_results": "\n".join(
                    f"ペルソナ: {i.persona.name} - {i.persona.background}\n"
                    f"質問: {i.question}\n"
                    f"回答: {i.answer}\n"
                    for i in interviews
                ),
            }
        )
