import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import fitz
import json

class PDFUploader:
    def __init__(self, api_url, max_workers=5):
        self.api_url = api_url
        self.max_workers = max_workers

    def load_manifest(self, manifest_path):
        """Load the manifest from the JSON file."""
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading manifest from {manifest_path}: {e}")
        return None

    def upload_pdf(self, file_path, manifest):
        """Upload a single PDF file to the API."""
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (file_path, file, 'application/pdf')}
                response = requests.post(self.api_url, files=files)
                return {
                    "file_path": file_path,
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code,
                    "response": response.json() if response.headers.get('Content-Type') == 'application/json' else response.text,
                    "manifest": manifest
                }
        except Exception as e:
            return {
                "file_path": file_path,
                "status": "error",
                "status_code": None,
                "response": str(e),
                "manifest": manifest
            }

    def upload_all_pdfs(self, folder_path):
        """Upload all PDF files in the specified folder to the API in parallel."""
        pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pdf = {executor.submit(self.upload_pdf, pdf_file, self.load_manifest(pdf_file.replace('.pdf', '.json'))): pdf_file for pdf_file in pdf_files}
            for future in as_completed(future_to_pdf):
                pdf_file = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    results.append({
                        "file_path": pdf_file,
                        "status": "error",
                        "status_code": None,
                        "response": str(exc),
                        "manifest": None
                    })

        return results

if __name__ == "__main__":
    api_url = "http://localhost:8000/extract_tables"  # Replace with your FastAPI endpoint
    uploader = PDFUploader(api_url, max_workers=10)  # Adjust max_workers based on your requirements
    results = uploader.upload_all_pdfs("data")  # Upload all PDFs in the 'data' folder

    # Print summary
    for result in results:
        print(f"File: {result['file_path']}")
        print(f"Status: {result['status']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Response: {result['response']}")
        print(f"Manifest: {result['manifest']}")
        print("-" + "=" * 30 + "-")
