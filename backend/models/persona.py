from pydantic import BaseModel, Field


class Persona(BaseModel):
    name: str = Field(..., description="名前")
    background: str = Field(..., description="背景")


class Personas(BaseModel):
    # default_factory=listは値が与えられなかった時に空のリストを返す
    personas: list[Persona] = Field(default_factory=list, description="人物")
