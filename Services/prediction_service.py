from typing import List

import numpy as np

from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest
from Dtos.Response.prediction_response import PredictionResponse, BatchPredictionResponse
from Models.model_loader import ModelLoader
from Services.logger_service import LoggerService


class PredictionService:
    def __init__(self):
        self.logger = LoggerService("prediction_service").get_logger()

    async def predict_single(self, request: PenguinInputRequest) -> PredictionResponse:
        try:
            loader = ModelLoader()
            result = await loader.load_model()

            if not result.success:
                self.logger.error(f"Failed to load model: {result.message}")
                return PredictionResponse(success=False, prediction=None, message="Model loading failed")

            model = result.model
            encoder = result.encoder

            features = np.array([[request.bill_length_mm, request.flipper_length_mm]])
            pred = model.predict(features)[0]
            pred_class = encoder.inverse_transform([pred])[0]

            self.logger.info(f"Single prediction: {pred_class}")

            return PredictionResponse(
                success=True,
                prediction=pred_class,
                message="Prediction successful"
            )

        except Exception as ex:
            self.logger.error(f"Single prediction failed: {str(ex)}")
            return PredictionResponse(success=False, prediction=None, message="Prediction error occurred")

    async def predict_batch(self, request: BatchInputRequest) -> BatchPredictionResponse:
        try:
            loader = ModelLoader()
            result = await loader.load_model()

            if not result.success:
                self.logger.error(f"Failed to load model: {result.message}")
                return BatchPredictionResponse(success=False, predictions=[], message="Model loading failed")

            model = result.model
            encoder = result.encoder

            features = np.array([
                [record.bill_length_mm, record.flipper_length_mm]
                for record in request.records
            ])

            preds = model.predict(features)
            pred_classes = encoder.inverse_transform(preds)

            self.logger.info(f"Batch prediction: {pred_classes.tolist()}")

            return BatchPredictionResponse(
                success=True,
                predictions=pred_classes.tolist(),
                message="Batch prediction successful"
            )

        except Exception as ex:
            self.logger.error(f"Batch prediction failed: {str(ex)}")
            return BatchPredictionResponse(success=False, predictions=[], message="Batch prediction error occurred")
