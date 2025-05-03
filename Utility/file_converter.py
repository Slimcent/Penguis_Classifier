import io
import csv
import pandas as pd
from typing import List, Any
from datetime import datetime
from Enums.file_type_enum import FileExportType
from starlette.responses import StreamingResponse


class FileConverter:

    @staticmethod
    def convert(data: List[Any], export_format: FileExportType, title: str = "export") -> StreamingResponse:
        if not data:
            raise ValueError("No data to export")

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{title}_{timestamp}"

        if export_format == FileExportType.csv:
            return FileConverter._to_csv(data, filename)
        elif export_format == FileExportType.excel:
            return FileConverter._to_excel(data, filename)
        else:
            raise ValueError("Unsupported export format")

    @staticmethod
    def _to_csv(data_list: List[Any], filename: str) -> StreamingResponse:
        if not data_list:
            raise ValueError("No data to export")

        # Flatten data
        flattened = []
        for item in data_list:
            row = {}
            for key, value in item.dict().items():
                if isinstance(value, dict):
                    row.update({k: v for k, v in value.items()})
                else:
                    row[key] = value
            flattened.append(row)

        headers = flattened[0].keys()

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flattened)

        # Add metadata as a comment at the top
        metadata = {
            "record_count": len(data_list),
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        metadata_lines = [f"# {key}: {value}" for key, value in metadata.items()]
        metadata_str = "\n".join(metadata_lines) + "\n"

        final_output = io.BytesIO()
        final_output.write(metadata_str.encode())
        final_output.write(output.getvalue().encode())
        final_output.seek(0)

        return StreamingResponse(
            final_output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    @staticmethod
    def _to_excel(data_list: List[Any], filename: str) -> StreamingResponse:
        if not data_list:
            raise ValueError("No data to export")

        # Extract records
        export_data = []
        for item in data_list:
            row = {}
            for key, value in item.dict().items():
                if isinstance(value, dict):
                    row.update({k: v for k, v in value.items()})
                else:
                    row[key] = value
            export_data.append(row)

        df = pd.DataFrame(export_data)

        # Create metadata
        metadata = {
            "record_count": len(data_list),
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        metadata_df = pd.DataFrame([metadata])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Predictions")
            metadata_df.to_excel(writer, index=False, sheet_name="Metadata")

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
