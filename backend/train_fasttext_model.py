import os
from dotenv import load_dotenv
from app.services.train_fasttext import main as train_fasttext
from app.utils import get_preprocessed_texts 

load_dotenv()

if __name__ == "__main__":
    
    model_path = os.getenv("FASTTEXT_MODEL_PATH")
    config_path = os.getenv("FASTTEXT_CONFIG_PATH")
    
    train_fasttext(model_path, get_preprocessed_texts, config_path)