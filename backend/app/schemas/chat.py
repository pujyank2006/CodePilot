from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        min_length = 1,
        max_length = 10000,
        description = "The user's message to CodePilot"
    )


class ChatResponse(BaseModel):
    reply: str
    model: str