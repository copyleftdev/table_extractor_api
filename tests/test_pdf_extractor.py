import os
import json
import pytest
import requests
from deepdiff import DeepDiff

# Directory containing the PDFs and manifest files
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
API_URL = "http://localhost:8000/extract_tables"

def get_pdf_files():
    """Retrieve all PDF files from the data directory."""
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
    print(f"Found {len(files)} PDF files in {DATA_DIR}: {files}")
    return files

@pytest.mark.parametrize("pdf_file", get_pdf_files())
def test_pdf_extraction(pdf_file):
    """Test the extraction of tables from a PDF file."""
    pdf_path = os.path.join(DATA_DIR, pdf_file)
    manifest_path = pdf_path.replace(".pdf", ".json")

    print(f"Testing PDF: {pdf_file}")
    print(f"PDF Path: {pdf_path}")
    print(f"Manifest Path: {manifest_path}")

    # Ensure the file is a valid PDF
    with open(pdf_path, 'rb') as f:
        file_signature = f.read(4)
        assert file_signature[:4] == b'%PDF', f"{pdf_path} is not a valid PDF file."

    # Read the manifest file
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    print(f"Manifest Data: {json.dumps(manifest, indent=2)}")

    # Upload the PDF and get the response
    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_file, f, 'application/pdf')}
        response = requests.post(API_URL, files=files)
        print(f"Uploaded {pdf_file}, Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content.decode('utf-8')}")

    assert response.status_code == 200, f"Failed with status code {response.status_code}"
    response_json = response.json()

    # Compare the response with the manifest
    assert "tables" in response_json, "Response does not contain 'tables'"

    extracted_tables = json.loads(response_json["tables"])
    print(f"Extracted Tables: {json.dumps(extracted_tables, indent=2)}")

    # Perform a detailed comparison using deepdiff
    diff = DeepDiff(manifest["sample_data"], extracted_tables, ignore_order=True)
    assert not diff, f"Differences found: {diff}"

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
