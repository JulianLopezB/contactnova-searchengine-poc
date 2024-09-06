import os
from dotenv import load_dotenv
from app.services.train_fasttext import main as train_fasttext
from app.services.data_ingestion import DataIngestionService

load_dotenv()

def get_preprocessed_texts():
    # This is a simplified version. You might need to adjust this based on your actual data ingestion process.
    data_ingestion_service = DataIngestionService(os.getenv("EXCEL_FILE_PATH"))
    return data_ingestion_service.get_preprocessed_texts()

if __name__ == "__main__":
    model_path = os.getenv("FASTTEXT_MODEL_PATH")
    config_path = os.getenv("FASTTEXT_CONFIG_PATH")

    train_fasttext(model_path, get_preprocessed_texts, config_path)