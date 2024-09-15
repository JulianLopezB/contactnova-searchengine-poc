import os
import logging
from dotenv import load_dotenv
from search_engine.ingestion.data_ingestion import DataIngestionService
from search_engine.utils.config import load_config
from search_engine.utils.data_preprocessor import load_training_data
from search_engine.embeddings.fasttext_embedding import FastTextEmbedding
from search_engine.embeddings.transformer_embedding import TransformerEmbedding

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def get_embedding_model(config):
    embedding_type = config['embedding']['type']
    embedding_config = config['embedding']['config']
    training_data_path = config['embedding'].get('training_data_path')

    logger.info(f"Loading training data from {training_data_path}")
    training_data = load_training_data(training_data_path)
    logger.info(f"Loaded {len(training_data)} training samples")

    if embedding_type == 'fasttext':
        logger.info("Initializing FastText embedding model")
        return FastTextEmbedding(embedding_config, training_data)
    elif embedding_type == 'transformer':
        logger.info("Initializing Transformer embedding model")
        return TransformerEmbedding(embedding_config, training_data)
    else:
        raise ValueError(f"Unsupported embedding type: {embedding_type}")

def implement_engine():
    logger.info("Starting engine implementation")

    # Load configuration
    config_path = os.getenv("CONFIG_FILE_PATH")
    if not config_path:
        raise ValueError("CONFIG_FILE_PATH environment variable is not set")
    
    logger.info(f"Loading configuration from {config_path}")
    config = load_config(config_path)
    logger.info("Configuration loaded successfully")

    # Initialize and train (if needed) the embedding model
    logger.info("Initializing embedding model")
    embedding_model = get_embedding_model(config)
    logger.info("Embedding model initialized successfully")

    # Ingest data
    logger.info("Starting data ingestion process")
    data_ingestion = DataIngestionService(embedding_model)
    data_ingestion.ingest_data()
    logger.info("Data ingestion completed")


    logger.info("Engine implementation completed successfully")

if __name__ == "__main__":
    try:
        implement_engine()
    except Exception as e:
        logger.exception("An error occurred during engine implementation")
        raise