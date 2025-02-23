from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.persona import Persona
from models.interview import Interview, InterviewResult


class InterviewConductor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, user_request: str, personas: list[Persona]) -> InterviewResult:
        questions = self._generate_questions(
            user_request=user_request, personas=personas
        )

        answers = self._generate_answers(
            personas=personas,
            questions=questions,
        )

        interviews = self._generate_interviews(
            personas=personas, questions=questions, answers=answers
        )

        return InterviewResult(interviews=interviews)

    def _generate_questions(
        self, user_request: str, personas: list[Persona]
    ) -> list[str]:
        question_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはユーザー要件に基づいて適切な質問を生成する専門家です。",
                ),
                (
                    "human",
                    "以下のペルソナに関連するユーザーリクエストについて、１つ質問を生成してください。\n\n"
                    "ユーザーリクエスト：{user_request}\n"
                    "ペルソナ：{persona_name} - {persona_background}\n\n"
                    "質問は具体的で、このペルソナの視点から重要な情報を引き出すように設計してください。",
                ),
            ]
        )

        question_chain = question_prompt | self.llm | StrOutputParser()

        question_queries = [
            {
                "persona_name": persona.name,
                "persona_background": persona.background,
                "user_request": user_request,
            }
            for persona in personas
        ]

        result = question_chain.batch(question_queries)
        return result

    def _generate_answers(
        self, personas: list[Persona], questions: list[str]
    ) -> list[str]:
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたは以下のペルソナとして回答しています：{persona_name} - {persona_background}",
                ),
                ("human", "質問：{question}\n"),
            ]
        )

        answer_chain = answer_prompt | self.llm | StrOutputParser()

        answer_queries = [
            {
                "persona_name": persona.name,
                "persona_background": persona.background,
                "question": question,
            }
            for persona, question in zip(personas, questions)
        ]

        return answer_chain.batch(answer_queries)

    def _generate_interviews(
        self, personas: list[Persona], questions: list[str], answers: list[str]
    ) -> list[Interview]:
        return [
            Interview(persona=persona, question=question, answer=answer)
            for persona, question, answer in zip(personas, questions, answers)
        ]
