from fastapi import FastAPI, Depends
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from functools import lru_cache

from agents.documentation_agent import DocumentationAgent

app = FastAPI()


@lru_cache()
def get_llm():
    return ChatOpenAI()


def get_documentation_agent(llm: ChatOpenAI = Depends(get_llm)) -> DocumentationAgent:
    return DocumentationAgent(llm)


class UserRequest(BaseModel):
    request: str


@app.post("/generate-requirements")
async def generate_requirements(
    user_request: UserRequest,
    documentation_agent: DocumentationAgent = Depends(get_documentation_agent),
):
    requirements_doc = documentation_agent.run(user_request.request)
    return {"requirements_doc": requirements_doc}
