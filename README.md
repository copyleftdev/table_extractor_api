# table_extractor_api

[![GitHub issues](https://img.shields.io/github/issues/copyleftdev/table_extractor_api)](https://github.com/copyleftdev/table_extractor_api/issues)
[![GitHub forks](https://img.shields.io/github/forks/copyleftdev/table_extractor_api)](https://github.com/copyleftdev/table_extractor_api/network)
[![GitHub stars](https://img.shields.io/github/stars/copyleftdev/table_extractor_api)](https://github.com/copyleftdev/table_extractor_api/stargazers)
[![GitHub license](https://img.shields.io/github/license/copyleftdev/table_extractor_api)](https://github.com/copyleftdev/table_extractor_api/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/copyleftdev/table_extractor_api/ci.yml)](https://github.com/copyleftdev/table_extractor_api/actions)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.95.2-green)
![Docker](https://img.shields.io/badge/docker-20.10.7-blue)
![Redis](https://img.shields.io/badge/redis-6.2.6-red)

## Table Extractor API

A FastAPI-based service for extracting tables from PDF files. The service supports extracting tables, rate limiting, and retrieving previously processed results.

## Features

- Extract tables from PDF files.
- Rate limiting to prevent abuse.
- Retrieve previously processed results.
- Support for uploading multiple files with pagination (TODO).
- OAuth2 authentication (TODO).

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/copyleftdev/table_extractor_api.git
    cd table_extractor_api
    ```

2. Build and start the Docker containers:
    ```bash
    docker-compose up --build
    ```

### API Endpoints

#### Extract Tables from PDF

```bash
curl -X 'POST' \
  'http://localhost:8000/extract_tables' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/file.pdf'
```

#### Retrieve Extraction Result by ID

```bash
curl -X 'GET' \
  'http://localhost:8000/result/{result_id}' \
  -H 'accept: application/json'
```

### Development

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the development server:
    ```bash
    uvicorn app.api:app --reload
    ```


## Technology Stack

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.95.2-green)
![Docker](https://img.shields.io/badge/docker-20.10.7-blue)
![Redis](https://img.shields.io/badge/redis-6.2.6-red)
