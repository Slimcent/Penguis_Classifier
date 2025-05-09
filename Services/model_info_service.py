import json
from Services.logger_service import LoggerService
from Core.global_model_loader import model_loader
from Dtos.Response.model_response import ModelInfoResponse
from Dtos.Response.service_response import ServiceResponse
from Services.redis_service import RedisService
from Infrastructure.app_constants import AppConstants


class ModelInfoService:
    def __init__(self):
        self.logger = LoggerService("prediction_service").get_logger()
        self.constants = AppConstants

    async def get_model_info(self) -> ServiceResponse[ModelInfoResponse]:
        try:
            # Get RedisService singleton instance
            redis_service = await RedisService.get_instance()

            # Try to get cached model info
            cached = await redis_service.read_from_cache(self.constants.model_info_key, compressed=True)
            if cached:
                self.logger.info("Model info retrieved from cache.")
                return ServiceResponse(success=True, message="Loaded from cache", data=ModelInfoResponse(**cached))

            # Load model if not already loaded
            if not model_loader.is_loaded():
                await model_loader.load_model()

            result = model_loader.get_info_response()
            if not result:
                return ServiceResponse(success=False, message="Model info is not available", data=None)

            # Save to cache (convert result to dictionary before storing)
            model_info_dict = result.dict()
            self.logger.info(f"Caching model info: {json.dumps(result.model_dump(), indent=2)} {model_info_dict}")

            await redis_service.write_to_cache(
                key=self.constants.model_info_key,
                value=model_info_dict,
                compress=True,
                ex=self.constants.cache_expiry
            )

            self.logger.info("Model info loaded and cached.")
            return ServiceResponse(success=True, message="Model info loaded successfully", data=result)

        except Exception as ex:
            self.logger.error(f"Error retrieving model info: {ex}")
            return ServiceResponse(success=False, message=str(ex), data=None)
