from pydantic import BaseModel

class Body(BaseModel):
    question: str
    history: list[dict[str, str]]