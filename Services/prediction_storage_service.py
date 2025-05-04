import io
import os
import csv
import aiofiles
import pandas as pd
from datetime import datetime
from typing import Union, List, Dict
from Services.logger_service import LoggerService
from Core.global_model_loader import model_loader
from Infrastructure.app_constants import AppConstants
from Dtos.Response.prediction_response import PredictionResponse
from Dtos.Request.penguin_input_request import PenguinInputRequest


class PredictionStorageService:
    def __init__(self):
        self.logger = LoggerService("prediction_storage_service").get_logger()
        self.encoder = None
        self.class_labels = []
        self.constants = AppConstants
        self.storage_folder = self.constants.base_folder
        os.makedirs(self.storage_folder, exist_ok=True)
        self.csv_path = os.path.join(self.storage_folder, f"{self.constants.prediction_storage_base}.csv")
        self.excel_path = os.path.join(self.storage_folder, f"{self.constants.prediction_storage_base}.xlsx")

    async def ensure_model_loaded(self):
        if not model_loader.is_loaded():
            result = await model_loader.load_model()
            if result:
                self.encoder = model_loader.get_label_encoder()
                self.class_labels = self.encoder.classes_.tolist()
            else:
                raise Exception("Model loading failed. Can't proceed with prediction.")
        elif not self.encoder or not self.class_labels:
            self.encoder = model_loader.get_label_encoder()
            self.class_labels = self.encoder.classes_.tolist()

    async def save_single_prediction(self, features: PenguinInputRequest, prediction: PredictionResponse) -> bool:
        await self.ensure_model_loaded()
        rows = self.build_rows([features], [prediction])
        return await self.save_predictions(rows)

    async def save_batch_prediction(self, batch_features: List[PenguinInputRequest],
                                    batch_predictions: List[PredictionResponse]) -> bool:
        await self.ensure_model_loaded()
        rows = self.build_rows(batch_features, batch_predictions)
        return await self.save_predictions(rows)

    def build_rows(self, features_list: List[PenguinInputRequest], predictions_list: List[PredictionResponse]) \
            -> List[Dict[str, Union[str, float]]]:
        print("entered build rows")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []
        for features, prediction in zip(features_list, predictions_list):
            row = {
                "bill_length_mm": features.bill_length_mm,
                "flipper_length_mm": features.flipper_length_mm,
                "prediction": prediction.prediction,
                **{label: round(prediction.probabilities.get(label, 0.0), 2) for label in self.class_labels},
                "model_version": self.constants.model_version,
                "prediction_timestamp": timestamp
            }
            rows.append(row)

        print("finished build rows")
        return rows

    async def save_predictions(self, rows: List[Dict]) -> bool:
        existing_rows = await self.read_existing_rows()

        normalized_existing = [normalize_row(r) for r in existing_rows]
        normalized_new = [normalize_row(r) for r in rows]

        new_rows = [rows[i] for i, r in enumerate(normalized_new) if r not in normalized_existing]

        if not new_rows:
            self.logger.info("No new predictions to append. All entries are duplicates.")
            return False

        await self.append_to_csv(new_rows)
        await self.write_to_excel()
        self.logger.info(f"Saved {len(new_rows)} new predictions.")
        return True

    async def read_existing_rows(self) -> List[Dict]:
        if not os.path.exists(self.csv_path):
            return []

        try:
            df = pd.read_csv(self.csv_path)
            return df[self.csv_headers()].to_dict(orient='records')
        except Exception as e:
            self.logger.warning(f"Could not read existing rows: {e}")
            return []

    async def append_to_csv(self, rows: List[Dict]):
        file_exists = os.path.exists(self.csv_path)
        buffer = None

        try:
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=self.csv_headers())

            if not file_exists:
                writer.writeheader()

            for row in rows:
                writer.writerow(row)

            # Write the buffered content to file asynchronously
            async with aiofiles.open(self.csv_path, mode='a', encoding='utf-8') as f:
                await f.write(buffer.getvalue())

            self.logger.info(f"Successfully appended {len(rows)} rows to {self.csv_path}")
        except Exception as e:
            self.logger.error(f"Failed to append to CSV file {self.csv_path}: {e}")
        finally:
            if buffer:
                buffer.close()
                self.logger.debug("CSV buffer closed successfully.")

    async def write_to_excel(self):
        try:
            df = pd.read_csv(self.csv_path)
            df.insert(0, 'id', range(1, len(df) + 1))
            df.to_excel(self.excel_path, index=False)
            self.logger.info(f"Excel file successfully written to {self.excel_path} with total rows now {len(df)}.")
        except Exception as e:
            self.logger.error(f"Failed to write Excel file: {e}")

    def csv_headers(self) -> List[str]:
        return [
            "bill_length_mm",
            "flipper_length_mm",
            "prediction",
            *self.class_labels,
            "model_version",
            "prediction_timestamp"
        ]


def normalize_row(row: Dict) -> Dict:
    return {
        k: str(v).strip()
        for k, v in row.items()
        if k != "prediction_timestamp"
    }

