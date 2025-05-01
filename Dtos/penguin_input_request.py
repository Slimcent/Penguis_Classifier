from pydantic import BaseModel


class PenguinInputRequest(BaseModel):
    bill_length_mm: float
    flipper_length_mm: float
