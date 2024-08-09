# ContactNova Search Engine POC - Backend

This is the backend component of the ContactNova Search Engine POC, built with FastAPI.

## Features

- Vector-based search using Qdrant
- FastText model for text embedding
- Data ingestion from Excel files
- Dockerized application for easy deployment

## Prerequisites

- Python 3.9+
- Docker (optional)

## Setup and Running

### Using Docker (recommended)

1. Build and run using Docker Compose:
   ```
   docker-compose up --build
   ```

2. The API will be available at `http://localhost:8000`.

### Without Docker

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the data ingestion script:
   ```
   python ingest_data.py /path/to/your/bc_datos.xlsx
   ```

3. Start the FastAPI server:
   ```
   python run.py
   ```

4. The API will be available at `http://localhost:8000`.

## API Endpoints

- `/search`: Perform a vector search
- `/categories`: Get available categories

For detailed API documentation, visit `http://localhost:8000/docs` after starting the application.

## Development

- Main application code is in the `app` directory
- API routes are defined in `app/api/routes/search.py`
- Core search functionality is in `app/services/search_service.py`

## License

This project is licensed under the MIT License.