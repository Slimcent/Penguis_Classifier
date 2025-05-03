from typing import List
from pydantic import BaseModel
from fastapi.params import File
from fastapi import UploadFile, Form
from Enums.file_type_enum import FileExportType


class PenguinInputRequest(BaseModel):
    bill_length_mm: float
    flipper_length_mm: float


class BatchInputRequest(BaseModel):
    records: List[PenguinInputRequest]


class DownloadPenguinPredictionsRequest:
    def __init__(
        self,
        file: UploadFile = File(...),
        file_type: FileExportType = Form(...)
    ):
        self.file = file
        self.file_type = file_type
