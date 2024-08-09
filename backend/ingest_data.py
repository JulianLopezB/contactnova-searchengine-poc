import os
import sys
from app.services.data_ingestion import DataIngestionService

def main(file_path: str):
    try:
        data_ingestion_service = DataIngestionService()
        data_ingestion_service.ingest_data(file_path)
        print("Data ingestion completed successfully.")
    except Exception as e:
        print(f"An error occurred during data ingestion: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_data.py <path_to_excel_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    
    main(file_path)