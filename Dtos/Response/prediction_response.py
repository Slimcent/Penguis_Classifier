from pydantic import BaseModel
from typing import Dict, List


class PredictionResponse(BaseModel):
    prediction: str
    probabilities: Dict[str, float]


class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]