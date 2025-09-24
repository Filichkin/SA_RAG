from pydantic import BaseModel


class AskWithAIResponse(BaseModel):
    query: str
