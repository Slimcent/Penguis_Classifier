from fastapi import APIRouter
from typing import List

from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest
from Dtos.Response.prediction_response import PredictionResponse, BatchPredictionResponse
from Services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["Prediction"])
prediction_service = PredictionService()


@router.post("/single", response_model=PredictionResponse)
async def predict_single_penguin(request: PenguinInputRequest):
    return await prediction_service.predict_single(request)


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch_penguins(request: BatchInputRequest):
    return await prediction_service.predict_batch(request)
