from pydantic import BaseModel, Field
from .persona import Persona


class Interview(BaseModel):
    persona: Persona = Field(..., description="人物")
    question: str = Field(..., description="質問")
    answer: str = Field(..., description="回答")


class InterviewResult(BaseModel):
    interviews: list[Interview] = Field(
        default_factory=list, description="インタビュー"
    )


class InterviewState(BaseModel):
    user_request: str = Field(..., description="ユーザーのリクエスト")
    personas: list[Persona] = Field(
        default_factory=list, description="生成されたペルソナのリスト"
    )
    interviews: list[Interview] = Field(
        default_factory=list, description="生成されたインタビューのリスト"
    )
    requirements_doc: str = Field(default="", description="生成された要件定義書")
    iteration: int = Field(
        default=0, description="ペルソナ生成とインタビューの反復回数"
    )
    is_information_sufficient: bool = Field(
        default=False, description="情報が十分かどうか"
    )
