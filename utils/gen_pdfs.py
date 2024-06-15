import os
import random
import string
import uuid
from datetime import datetime
import json
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Create the data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

class PDFTableGenerator:
    def __init__(self, num_rows, num_columns):
        self.num_rows = num_rows
        self.num_columns = num_columns

    def generate_random_data(self):
        """Generate a DataFrame with random data."""
        data = {
            f"Column {i+1}": [self._random_string(10) for _ in range(self.num_rows)]
            for i in range(self.num_columns)
        }
        return pd.DataFrame(data)

    def _random_string(self, length):
        """Generate a random string of fixed length."""
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(length))

    def create_pdf(self, df, pdf_filename):
        """Create a PDF with the given DataFrame."""
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []

        # Create table data
        data = [df.columns.tolist()] + df.values.tolist()

        # Create Table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        pdf.build(elements)

    def generate_pdf_with_table(self):
        """Generate a random PDF file with a table and a manifest."""
        df = self.generate_random_data()
        guid = str(uuid.uuid4())
        pdf_filename = f"data/{guid}.pdf"
        manifest_filename = f"data/{guid}.json"
        manifest = {
            "guid": guid,
            "timestamp": datetime.now().isoformat(),
            "num_rows": self.num_rows,
            "num_columns": self.num_columns,
            "data_summary": df.describe().to_dict(),
            "sample_data": df.head(3).to_dict(orient="records"),
            "tables": df.to_dict(orient="records")
        }
        self.create_pdf(df, pdf_filename)
        
        # Save manifest as JSON file
        with open(manifest_filename, "w") as f:
            json.dump(manifest, f, indent=4)
        
        print(f"Generated {pdf_filename} and {manifest_filename}")

if __name__ == "__main__":
    # Example: Generate 5 PDFs with random tables
    for _ in range(888):
        num_rows = random.randint(5, 15)  # Random number of rows between 5 and 15
        num_columns = random.randint(3, 8)  # Random number of columns between 3 and 8
        generator = PDFTableGenerator(num_rows, num_columns)
        generator.generate_pdf_with_table()
