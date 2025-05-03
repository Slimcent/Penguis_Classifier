from fastapi import APIRouter
from Services.model_info_service import ModelInfoService
from Dtos.Response.model_response import ModelInfoResponse
from Dtos.Response.service_response import ServiceResponse

router = APIRouter()
model_info_service = ModelInfoService()


@router.get("/penguin-info", summary="Penguin Model Info", description="Returns details about the training and model.",
            tags=["Overview"], response_model=ServiceResponse[ModelInfoResponse])
async def get_penguin_info():
    return await model_info_service.get_model_info()
