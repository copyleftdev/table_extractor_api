import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

import pdfplumber  # This is the new library for handling PDFs
import pandas as pd
import redis
import io

class PDFTableExtractor:
    """
    A class to extract tables from a PDF file.

    Attributes:
        file_content (bytes): The content of the PDF file.
        redis_client (redis.Redis): The Redis client for caching results.
    """
    def __init__(self, file_content: bytes, redis_client: redis.Redis):
        """
        Initialize the PDFTableExtractor with the given file content and Redis client.

        Args:
            file_content (bytes): The content of the PDF file.
            redis_client (redis.Redis): The Redis client for caching results.
        """
        self.file_content = file_content
        self.redis_client = redis_client

    @staticmethod
    def _format_table(table: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Format the table output as key-value pairs.

        Args:
            table (List[List[str]]): The extracted table.

        Returns:
            List[Dict[str, Any]]: The formatted table as a list of dictionaries.
        """
        df = pd.DataFrame(table[1:], columns=table[0])
        df.dropna(how="all", inplace=True, axis=1)
        return df.to_dict(orient="records")

    @staticmethod
    def _check_and_populate_cell_values(rows_bboxes, extracted_table: List[List[str]]) -> List[List[str]]:
        """
        Check and match the cell bounding boxes. If a cell exists, populate its value.
        If not, get the value from the previous row.

        Args:
            rows_bboxes: The bounding boxes of the rows.
            extracted_table (List[List[str]]): The extracted table.

        Returns:
            List[List[str]]: The table with populated cell values.
        """
        for row_index, row in enumerate(rows_bboxes):
            for col_index, cell in enumerate(row.cells):
                if not cell:
                    extracted_table[row_index][col_index] = extracted_table[row_index - 1][col_index]
        return extracted_table

    def _extract_tables_from_page(self, page) -> List[Dict[str, Any]]:
        """
        Extract tables from a single page of the PDF.

        Args:
            page: The PDF page to extract tables from.

        Returns:
            List[Dict[str, Any]]: The extracted tables from the page.
        """
        if not page.extract_text():
            return []

        tables = []
        for table in page.extract_tables():
            table = self._format_table(table)
            tables.append(table)
        return tables

    def extract_tables(self) -> str:
        """
        Extract tables from the PDF file and return as JSON.

        Returns:
            str: The extracted tables as a JSON string.

        Example:
            ```
            extractor = PDFTableExtractor(file_content, redis_client)
            tables_json = extractor.extract_tables()
            ```
        """
        # Check if the result is cached in Redis
        cache_key = f"pdf_table:{hash(self.file_content)}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return cached_data.decode('utf-8')

        tables = []
        try:
            # Open the PDF from bytes
            with pdfplumber.open(io.BytesIO(self.file_content)) as pdf:
                with ThreadPoolExecutor() as executor:
                    future_to_page = {executor.submit(self._extract_tables_from_page, page): page for page in pdf.pages}
                    for future in future_to_page:
                        result = future.result()
                        if result:
                            tables.extend(result)
        except Exception as e:
            return json.dumps({"error": f"An error occurred: {e}"})

        tables_json = json.dumps(tables)
        # Cache the result in Redis
        self.redis_client.set(cache_key, tables_json)

        return tables_json
