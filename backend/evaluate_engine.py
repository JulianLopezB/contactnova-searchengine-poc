import argparse
import logging
from dotenv import load_dotenv
from search_engine.embeddings.fasttext_embedding import FastTextEmbedding
from search_engine.embeddings.transformer_embedding import TransformerEmbedding
from search_engine.evaluation.evaluator import Evaluator
from search_engine.utils.config import load_config
from search_engine.utils.data_preprocessor import load_training_data
import mlflow

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_embedding_model(config):
    embedding_type = config['embedding']['type']
    logger.info(f"Loading training data from {config['embedding'].get('training_data_path')}")
    training_data = load_training_data(config['embedding'].get('training_data_path'))
    logger.info(f"Loaded {len(training_data)} training samples")

    if embedding_type == 'fasttext':
        logger.info("Initializing FastText embedding model")
        return FastTextEmbedding(config['embedding']['config'], training_data)
    elif embedding_type == 'transformer':
        logger.info("Initializing Transformer embedding model")
        return TransformerEmbedding(config['embedding']['config'], training_data)
    else:
        raise ValueError(f"Unsupported embedding type: {embedding_type}")

def evaluate_engine(config_path):
    logger.info(f"Loading configuration from {config_path}")
    config = load_config(config_path)

    logger.info("Initializing embedding model")
    embedding = get_embedding_model(config)

    logger.info(f"Setting up MLflow experiment: {config['mlflow']['experiment_name']}")
    mlflow.set_experiment(config['mlflow']['experiment_name'])

    with mlflow.start_run():
        logger.info("Starting evaluation")
        evaluator = Evaluator(embedding)
        logger.info(f"Evaluating with articles file: {config['evaluation']['articles_file']}")
        logger.info(f"Evaluating with rankings file: {config['evaluation']['rankings_file']}")
        results = evaluator.evaluate(config['evaluation']['articles_file'], config['evaluation']['rankings_file'])

        logger.info("Logging parameters and metrics to MLflow")
        mlflow.log_params({"embedding_type": config['embedding']['type'], **config['embedding']['config']})
        
        for metric_name, metric_value in results.items():
            logger.info(f"Logging metric: {metric_name} = {metric_value}")
            mlflow.log_metric(metric_name, metric_value)

        logger.info(f"{config['embedding']['type'].capitalize()} Evaluation Results:")
        for metric_name, metric_value in results.items():
            logger.info(f"{metric_name}: {metric_value}")

    return embedding

if __name__ == "__main__":
  #  parser = argparse.ArgumentParser(description="Evaluate search engine embeddings")
   # parser.add_argument("config", help="Path to configuration file")
    #args = parser.parse_args()

    #logger.info(f"Starting evaluation with config file: {args.config}")
    evaluate_engine(f'config/fasttext_config.yaml')
    logger.info("Evaluation completed")