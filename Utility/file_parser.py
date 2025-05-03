import io
import pandas as pd
from typing import List
from fastapi import UploadFile
from Services.logger_service import LoggerService
from Dtos.Request.penguin_input_request import PenguinInputRequest


class FileParser:
    logger = LoggerService("FileParser").get_logger()

    @staticmethod
    async def parse_penguin_file(file: UploadFile) -> List[PenguinInputRequest]:
        try:
            FileParser.logger.info(f"Starting to parse file: {file.filename}")

            contents = await file.read()
            df = None

            if file.filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            elif file.filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(contents))
            else:
                raise ValueError("Unsupported file type. Only CSV and Excel files are allowed.")

            # Log the number of rows in the file
            FileParser.logger.info(f"Loaded file: {file.filename} with {len(df)} rows.")

            # Check if required columns are present
            required_columns = {"bill_length_mm", "flipper_length_mm"}
            if not required_columns.issubset(df.columns):
                raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")

            return [
                PenguinInputRequest(
                    bill_length_mm=row["bill_length_mm"],
                    flipper_length_mm=row["flipper_length_mm"]
                )
                for _, row in df.iterrows()
            ]

        except Exception as ex:
            FileParser.logger.error(f"File parsing failed for {file.filename}: {str(ex)}")
            raise ValueError("Failed to parse input file.")
