from starlette.responses import StreamingResponse
from fastapi import APIRouter, UploadFile, Depends
from Services.prediction_service import PredictionService
from Dtos.Response.service_response import ServiceResponse
from Dtos.Response.prediction_response import PredictionResponse, BatchPredictionResponse
from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest, DownloadPenguinPredictionsRequest

router = APIRouter()
prediction_service = PredictionService()


@router.post("/predict-single", response_model=ServiceResponse[PredictionResponse])
async def predict_single_penguin(request: PenguinInputRequest):
    return await prediction_service.predict_single(request)


@router.post("/predict-batch", response_model=ServiceResponse[BatchPredictionResponse])
async def predict_batch_penguins(request: BatchInputRequest):
    return await prediction_service.predict_batch(request)


@router.post("/predict-from-file", response_model=ServiceResponse[BatchPredictionResponse])
async def predict_from_file(file: UploadFile):
    response = await prediction_service.predict_from_file(file)
    return response


@router.post("/download-predictions", response_model=None)
async def download_predictions(request: DownloadPenguinPredictionsRequest = Depends()) -> StreamingResponse:
    return await prediction_service.download_penguin_predictions(request.file, request.file_type)
