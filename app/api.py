from fastapi import FastAPI, File, UploadFile, HTTPException, Request
import redis
from .pdf_extractor import PDFTableExtractor
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uuid
import logging
import os
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI()

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Configure logging
logging.basicConfig(level=logging.INFO)

class ExtractionResponse(BaseModel):
    tables: str

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

@app.post("/extract_tables", response_model=List[ExtractionResponse])
@limiter.limit("5/minute")
async def extract_tables_from_pdf(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """
    Extract tables from the uploaded PDF files.

    Args:
        files (List[UploadFile]): The PDF files to extract tables from.

    Returns:
        List[dict]: A list of dictionaries containing the extracted tables.

    Raises:
        HTTPException: If any file type is not PDF or any error occurs during extraction.
    """
    results = []

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
        
        # Log the file upload attempt
        logging.info(f"Received file: {file.filename}, content_type: {file.content_type}")

        try:
            file_content = await file.read()
            extractor = PDFTableExtractor(file_content, redis_client)
            tables = extractor.extract_tables()
            
            # Generate unique ID and save result to Redis
            result_id = str(uuid.uuid4())
            redis_client.set(result_id, tables)
            
            # Create response
            result = {"tables": tables}
            results.append(result)
            
            # Save response to a file (optional, for debugging)
            with open(f"/tmp/{result_id}.json", "w") as f:
                f.write(tables)
            
            logging.info(f"Processed file: {file.filename}, saved result with ID: {result_id}")
        except Exception as e:
            logging.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    return results

@app.get("/")
@limiter.limit("10/minute")
async def read_root(request: Request):
    """
    Root endpoint to check the service status.

    Returns:
        dict: A welcome message.

    Example:
        ```
        curl -X 'GET' 'http://localhost:8000/'
        ```
    """
    return {"message": "Welcome to the PDF Table Extractor! Upload a PDF to extract tables."}

@app.get("/result/{result_id}", response_model=ExtractionResponse)
@limiter.limit("5/minute")
async def get_extraction_result(request: Request, result_id: str):
    """
    Retrieve the result of a previously processed PDF extraction by result ID.

    Args:
        result_id (str): The unique ID of the extraction result.

    Returns:
        dict: The extraction result.

    Raises:
        HTTPException: If the result is not found.
    """
    result = redis_client.get(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return JSONResponse(content={"tables": result.decode('utf-8')})
