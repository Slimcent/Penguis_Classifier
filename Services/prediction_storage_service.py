import io
import json
import os
import csv
import base64
import aiofiles
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, List, Dict
from Services.logger_service import LoggerService
from Core.global_model_loader import model_loader
from Services.github_uploader import GitHubUploader
from Infrastructure.app_constants import AppConstants
from Dtos.Response.prediction_response import PredictionResponse
from Dtos.Request.penguin_input_request import PenguinInputRequest

load_dotenv()


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
        self.github_uploader = GitHubUploader()

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

    async def save_single_prediction_to_github(self, features: PenguinInputRequest,
                                               prediction: PredictionResponse) -> bool:
        await self.ensure_model_loaded()
        rows = self.build_rows([features], [prediction])
        return await self.upload_prediction_to_github(rows)

    async def save_batch_prediction_to_github(self, batch_features: List[PenguinInputRequest],
                                              batch_predictions: List[PredictionResponse]) -> bool:
        await self.ensure_model_loaded()
        rows = self.build_rows(batch_features, batch_predictions)
        return await self.upload_prediction_to_github(rows)

    async def upload_prediction_to_github(self, rows: List[Dict]) -> bool:
        self.logger.info("Preparing prediction data for GitHub upload")

        # Fetch existing data
        self.logger.info("Fetching existing data from GitHub repository")
        existing_rows_csv = await self.github_uploader.get_existing_github_file_content(self.constants.github_csv_path)
        existing_rows_excel = await self.github_uploader.get_existing_github_file_content(
            self.constants.github_excel_path)

        # Deduplicate and merge
        self.logger.info("Deduplicating and merging prediction data")
        merged_rows_csv = deduplicate_rows(existing_rows_csv, rows, self.logger, "CSV")
        merged_rows_excel = deduplicate_rows(existing_rows_excel, rows, self.logger, "Excel")

        # Prepare contents
        self.logger.info("Preparing CSV and Excel contents for upload")
        csv_content = self.prepare_csv_content(merged_rows_csv)
        excel_content = self.prepare_excel_content(merged_rows_excel)

        # Upload CSV
        self.logger.info("Uploading CSV prediction file to GitHub")
        csv_uploaded = await self.github_uploader.upload_to_github(
            path=self.constants.github_csv_path,
            content=csv_content,
            is_binary=False
        )

        if csv_uploaded:
            self.logger.info("CSV prediction file uploaded successfully.")
        else:
            self.logger.error("Failed to upload CSV prediction file.")

        # Upload Excel
        self.logger.info("Uploading Excel prediction file to GitHub")
        excel_uploaded = await self.github_uploader.upload_to_github(
            path=self.constants.github_excel_path,
            content=excel_content,
            is_binary=True
        )

        if excel_uploaded:
            self.logger.info("Excel prediction file uploaded successfully.")
        else:
            self.logger.error("Failed to upload Excel prediction file.")

        return csv_uploaded and excel_uploaded

    def prepare_csv_content(self, rows: List[Dict]) -> str:
        headers = self.csv_headers()

        # Normalize and filter rows
        normalized_rows = [
            {header: str(row.get(header, "")).strip() for header in headers}
            for row in rows
        ]

        filtered_rows = [
            row for row in normalized_rows if any(value for value in row.values())
        ]

        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=headers)
        writer.writeheader()
        writer.writerows(filtered_rows)
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        return csv_content

    def prepare_excel_content(self, rows: List[Dict]) -> str:
        headers = self.csv_headers()

        # Normalize and filter rows
        normalized_rows = [
            {header: str(row.get(header, "")).strip() for header in headers}
            for row in rows
        ]

        filtered_rows = [
            row for row in normalized_rows if any(value for value in row.values())
        ]

        # Generate Excel content from filtered rows
        df = pd.DataFrame(filtered_rows, columns=headers)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        encoded_content = base64.b64encode(excel_buffer.read()).decode("utf-8")

        return encoded_content

    def compare_data(self, existing_rows: List[Dict], new_rows: List[Dict]) -> bool:
        # Exclude 'prediction_timestamp' from the headers during comparison
        excluded_header = 'prediction_timestamp'

        # Normalize both existing and new rows to make comparison easier
        existing_normalized = [
            {header: str(row.get(header, "")).strip() for header in self.csv_headers() if header != excluded_header}
            for row in existing_rows
        ]
        new_normalized = [
            {header: str(row.get(header, "")).strip() for header in self.csv_headers() if header != excluded_header}
            for row in new_rows
        ]

        # Check if new data already exists (excluding the 'prediction_timestamp' header)
        return existing_normalized != new_normalized


def normalize_row(row: Dict) -> Dict:
    return {
        k: str(v).strip()
        for k, v in row.items()
        if k != "prediction_timestamp"
    }


def deduplicate_rows(existing: List[Dict], new: List[Dict], logger, label: str) -> List[Dict]:
    existing_normalized = {
        json.dumps(normalize_row(row), sort_keys=True)
        for row in existing
    }

    unique_new = []
    duplicate_count = 0

    for row in new:
        normalized = json.dumps(normalize_row(row), sort_keys=True)
        if normalized not in existing_normalized:
            unique_new.append(row)
        else:
            duplicate_count += 1

    logger.info(f"{label}: {len(unique_new)} new rows added, {duplicate_count} duplicates skipped.")
    return existing + unique_new
