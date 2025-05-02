from fastapi import APIRouter
from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest
from Dtos.Response.prediction_response import PredictionResponse, BatchPredictionResponse
from Dtos.Response.service_response import ServiceResponse
from Services.prediction_service import PredictionService

router = APIRouter()
prediction_service = PredictionService()


@router.post("/single", response_model=ServiceResponse[PredictionResponse])
async def predict_single_penguin(request: PenguinInputRequest):
    return await prediction_service.predict_single(request)


@router.post("/batch", response_model=ServiceResponse[BatchPredictionResponse])
async def predict_batch_penguins(request: BatchInputRequest):
    return await prediction_service.predict_batch(request)
