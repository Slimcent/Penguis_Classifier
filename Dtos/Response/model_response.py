from typing import Dict
from pydantic import BaseModel


class DataInfo(BaseModel):
    initial_rows: int
    cleaned_rows: int
    dropped_rows: int


class TrainingInfo(BaseModel):
    train_accuracy: float
    test_accuracy: float
    label_mapping: Dict[int, str]


class ModelInfoResponse(BaseModel):
    name: str
    description: str
    data_info: DataInfo
    training_info: TrainingInfo
