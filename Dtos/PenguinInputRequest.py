from pydantic import BaseModel


class PenguinInput(BaseModel):
    bill_length_mm: float
    flipper_length_mm: float
