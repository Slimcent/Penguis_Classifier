from typing import Dict, List
from pydantic import BaseModel


class PredictionResponse(BaseModel):
    prediction: str
    probabilities: Dict[str, float]


class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
