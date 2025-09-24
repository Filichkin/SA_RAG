from pydantic import BaseModel


class AskWithAIResponse(BaseModel):
    response: str
