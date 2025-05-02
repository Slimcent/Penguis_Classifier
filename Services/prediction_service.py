import json
from typing import List

import numpy as np

from Core.global_model_loader import model_loader
from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest
from Dtos.Response.prediction_response import PredictionResponse, BatchPredictionResponse
from Dtos.Response.service_response import ServiceResponse
from Models.model_loader import ModelLoader
from Services.logger_service import LoggerService


class PredictionService:
    def __init__(self):
        self.logger = LoggerService("prediction_service").get_logger()

    async def predict_single(self, request: PenguinInputRequest) -> ServiceResponse[PredictionResponse]:
        try:
            if not model_loader.is_loaded():
                result = await model_loader.load_model()
                if not result:
                    message = result.message if result else "Unknown model load failure"
                    self.logger.error(f"Failed to load model: {message}")
                    return ServiceResponse(success=False, message=message, data=None)

            model = model_loader.get_model()
            encoder = model_loader.get_label_encoder()

            features = np.array([[request.bill_length_mm, request.flipper_length_mm]])
            pred = model.predict(features)[0]
            proba = model.predict_proba(features)[0]
            class_labels = encoder.inverse_transform(np.arange(len(proba)))
            probabilities = {label: float(prob) for label, prob in zip(class_labels, proba)}

            prediction_data = PredictionResponse(
                prediction=encoder.inverse_transform([pred])[0],
                probabilities=probabilities
            )

            self.logger.info(f"\nSingle model predicted successfully: {json.dumps(prediction_data.model_dump(), indent=2)}")
            return ServiceResponse(success=True, message="Prediction completed successfully", data=prediction_data)

        except Exception as ex:
            self.logger.error(f"Single prediction failed: {str(ex)}")
            return ServiceResponse(success=False, message="Prediction error occurred", data=None)

    async def predict_batch(self, request: BatchInputRequest) -> ServiceResponse[BatchPredictionResponse]:
        try:
            if not model_loader.is_loaded():
                result = await model_loader.load_model()
                if not result:
                    message = result.message if result else "Unknown model load failure"
                    self.logger.error(f"Failed to load model: {message}")
                    return ServiceResponse(success=False, message=message, data=None)

            model = model_loader.get_model()
            encoder = model_loader.get_label_encoder()

            features = np.array([
                [record.bill_length_mm, record.flipper_length_mm]
                for record in request.records
            ])

            preds = model.predict(features)
            probas = model.predict_proba(features)

            class_labels = encoder.inverse_transform(np.arange(probas.shape[1]))

            results = []
            for pred, proba in zip(preds, probas):
                prediction_label = encoder.inverse_transform([pred])[0]
                probabilities = {
                    label: round(float(p), 2) for label, p in zip(class_labels, proba)
                }

                results.append(PredictionResponse(
                    prediction=prediction_label,
                    probabilities=probabilities
                ))

            self.logger.info(f"\nBatch model predicted successfully: {json.dumps(results.model_dump(), indent=2)}")
            return ServiceResponse(success=True, message="Batch prediction successful",
                                   data=BatchPredictionResponse(results=results))

        except Exception as ex:
            self.logger.error(f"Batch prediction failed: {str(ex)}")
            return ServiceResponse(success=False, message="Batch prediction error occurred", data=None)
