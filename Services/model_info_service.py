import json

from Core.global_model_loader import model_loader
from Dtos.Response.model_response import ModelInfoResponse
from Dtos.Response.service_response import ServiceResponse
from Models.model_loader import ModelLoader
from Services.logger_service import LoggerService


class ModelInfoService:
    def __init__(self):
        self.logger = LoggerService("prediction_service").get_logger()

    # async def get_model_info(self) -> ModelInfoResponse:
    #     try:
    #         loader = ModelLoader()
    #         result = await loader.load_model()
    #
    #         if not result:
    #             self.logger.error(f"Failed to load model info: {result.message}")
    #             print(f"{result.message}")
    #             return ModelInfoResponse(
    #                 name="",
    #                 description="",
    #                 data_info=None,
    #                 training_info=None
    #             )
    #
    #         print("returned penguin info")
    #         return result.model_info
    #
    #     except Exception as ex:
    #         self.logger.error(f"Error loading model info: {str(ex)}")
    #         return ModelInfoResponse(
    #             name="",
    #             description="",
    #             data_info=None,
    #             training_info=None
    #         )

    # async def get_model_info(self) -> ServiceResponse[ModelInfoResponse]:
    #     try:
    #         loader = ModelLoader()
    #         result = await loader.load_model()
    #
    #         print("loaded trained model")
    #
    #         if not result:
    #             message = getattr(result, 'message', 'Model info is missing or invalid')
    #             self.logger.error(f"Failed to load model info: {message}")
    #             return ServiceResponse(
    #                 success=False,
    #                 message=message,
    #                 data=None
    #             )
    #
    #         print("Returned penguin info")
    #         return ServiceResponse(
    #             success=True,
    #             message="Model info loaded successfully",
    #             data=result
    #         )
    #
    #     except Exception as ex:
    #         error_msg = f"Error loading model info: {str(ex)}"
    #         self.logger.error(error_msg)
    #         return ServiceResponse(
    #             success=False,
    #             message=error_msg,
    #             data=None
    #         )

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
