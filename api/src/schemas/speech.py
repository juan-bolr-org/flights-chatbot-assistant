from pydantic import BaseModel


class SpeechToTextResponse(BaseModel):
    text: str
    confidence: float = 1.0

