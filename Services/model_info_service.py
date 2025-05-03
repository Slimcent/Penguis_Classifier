import json
from Services.logger_service import LoggerService
from Core.global_model_loader import model_loader
from Dtos.Response.model_response import ModelInfoResponse
from Dtos.Response.service_response import ServiceResponse


class ModelInfoService:
    def __init__(self):
        self.logger = LoggerService("prediction_service").get_logger()

    async def get_model_info(self) -> ServiceResponse[ModelInfoResponse]:
        try:
            if not model_loader.is_loaded():
                await model_loader.load_model()

            result = model_loader.get_info_response()
            if not result:
                return ServiceResponse(success=False, message="Model info is not available", data=None)

            self.logger.info(f"\nModel info retrieved successfully: {json.dumps(result.model_dump(), indent=2)}")
            return ServiceResponse(success=True, message="Model info loaded successfully", data=result)

        except Exception as ex:
            error_msg = f"Error retrieving model info: {str(ex)}"
            self.logger.error(error_msg)
            return ServiceResponse(success=False, message=error_msg, data=None)
