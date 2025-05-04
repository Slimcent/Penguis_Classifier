import json
import numpy as np
from Utility.file_parser import FileParser
from fastapi import UploadFile, HTTPException
from Enums.file_type_enum import FileExportType
from Utility.file_converter import FileConverter
from starlette.responses import StreamingResponse
from Core.global_model_loader import model_loader
from Services.logger_service import LoggerService
from Dtos.Response.service_response import ServiceResponse
from Services.prediction_storage_service import PredictionStorageService
from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest
from Dtos.Response.prediction_response import PredictionResponse, BatchPredictionResponse


class PredictionService:
    def __init__(self):
        self.logger = LoggerService("prediction_service").get_logger()
        self.prediction_saver = PredictionStorageService()

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

            # local_prediction_save_success = await self.prediction_saver.save_single_prediction(request,
            # prediction_data)
            # if local_prediction_save_success:
            #     self.logger.info("Local prediction result saved successfully.")
            # else:
            #     self.logger.warning("Local prediction result was not saved (possibly duplicate or write failure).")

            github_prediction_save_success = await self.prediction_saver.save_single_prediction_to_github(request,
                                                                                prediction_data)
            if github_prediction_save_success:
                self.logger.info("Github prediction result saved successfully.")
            else:
                self.logger.warning("Github prediction result was not saved (possibly duplicate or write failure).")

            self.logger.info(
                f"\nSingle model predicted successfully: {json.dumps(prediction_data.model_dump(), indent=2)}")
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

            # local_prediction_save_success = await self.prediction_saver.save_batch_prediction(request.records,
            # results)
            # if local_prediction_save_success:
            #     self.logger.info("PLocal prediction result saved successfully.")
            # else:
            #     self.logger.warning("Local prediction result was not saved (possibly duplicate or write failure).")

            github_prediction_save_success = await self.prediction_saver.save_batch_prediction_to_github(
                request.records, results)
            if github_prediction_save_success:
                self.logger.info("Github prediction result saved successfully.")
            else:
                self.logger.warning("Github prediction result was not saved (possibly duplicate or write failure).")

            predictions_json = json.dumps([prediction.dict() for prediction in results], indent=2)
            self.logger.info(f"\nBatch model predicted successfully: {predictions_json}")
            return ServiceResponse(success=True, message="Batch prediction successful",
                                   data=BatchPredictionResponse(results=results))

        except Exception as ex:
            self.logger.error(f"Batch prediction failed: {str(ex)}")
            return ServiceResponse(success=False, message="Batch prediction error occurred", data=None)

    async def predict_from_file(self, file: UploadFile) -> ServiceResponse[BatchPredictionResponse]:
        try:
            records = await FileParser.parse_penguin_file(file)
            if not records:
                return ServiceResponse(success=False, message="No valid data found in the file", data=None)

            request = BatchInputRequest(records=records)
            response = await self.predict_batch(request)

            if response.success:
                predictions_json = json.dumps([prediction.dict() for prediction in response.data.results], indent=2)
                self.logger.info(f"Predictions from file: {predictions_json}")

            return response

        except Exception as ex:
            self.logger.error(f"File prediction failed: {str(ex)}")
            return ServiceResponse(success=False, message=str(ex), data=None)

    async def download_penguin_predictions(self, file: UploadFile, file_type: FileExportType) -> StreamingResponse:
        response = await self.predict_from_file(file)

        if not response.success or not response.data:
            self.logger.error(f"Prediction export failed: {response.message}")
            raise HTTPException(status_code=400, detail=response.message)

        predictions = response.data.results
        count = len(predictions)
        self.logger.info(f"Exporting {count} predictions to {file_type.value.upper()} format")

        return FileConverter.convert(predictions, file_type, "Penguin Prediction")
