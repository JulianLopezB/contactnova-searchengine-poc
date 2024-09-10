import os
import logging
import fasttext
import mlflow
import tempfile
import yaml
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class FastTextTrainer:
    def __init__(self, model_path, get_preprocessed_texts_func, config_path):
        self.model_path = model_path
        self.get_preprocessed_texts = get_preprocessed_texts_func
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def load_or_train_model(self):
        if not os.path.exists(self.model_path):
            logger.info(f"FastText model not found at {self.model_path}. Training new model.")
            return self.train_fasttext()
        else:
            try:
                return fasttext.load_model(self.model_path)
            except Exception as e:
                logger.error(f"Failed to load FastText model from {self.model_path}: {str(e)}")
                raise ValueError(f"Failed to load FastText model: {str(e)}")

    def train_fasttext(self):
        mlflow.set_experiment("FastText Training - Spanish")

        texts = self.get_preprocessed_texts()

        temp_file_path = None
        model_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
                for text in texts:
                    temp_file.write(f"{text}\n")
                temp_file_path = temp_file.name

            with mlflow.start_run():
                model = fasttext.train_unsupervised(
                    temp_file_path,
                    model=self.config['model'],
                    dim=self.config['dim'],
                    epoch=self.config['epoch'],
                    lr=self.config['lr'],
                    wordNgrams=self.config['wordNgrams'],
                    minn=self.config['minn'],
                    maxn=self.config['maxn'],
                    thread=self.config['thread']
                )

                # Calculate metrics
                semantic_similarity = self.evaluate_semantic_similarity(model)
                analogy_task = self.evaluate_analogy_task(model)
                word_similarity = self.evaluate_word_similarity(model)

                # Log parameters and metrics
                mlflow.log_params(self.config)
                mlflow.log_metric("semantic_similarity", semantic_similarity)
                mlflow.log_metric("analogy_task", analogy_task)
                mlflow.log_metric("word_similarity", word_similarity)

                # Log the model as an artifact
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as model_file:
                    model_file_path = model_file.name
                model.save_model(model_file_path)
                mlflow.log_artifact(model_file_path, "model")

            # Save the model outside of the mlflow run
            model.save_model(self.model_path)
            return model

        finally:
            # Clean up temporary files
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if model_file_path and os.path.exists(model_file_path):
                os.unlink(model_file_path)

    def evaluate_semantic_similarity(self, model):
        word_pairs = [
            ("gato", "perro"),
            ("feliz", "triste"),
            ("rey", "reina"),
            ("hombre", "mujer"),
            ("bueno", "malo")
        ]
        similarities = []
        for word1, word2 in word_pairs:
            vec1 = model.get_word_vector(word1)
            vec2 = model.get_word_vector(word2)
            similarity = cosine_similarity([vec1], [vec2])[0][0]
            similarities.append(similarity)
        return np.mean(similarities)

    def evaluate_analogy_task(self, model):
        analogies = [
            ("hombre", "mujer", "rey", "reina"),
            ("madrid", "españa", "parís", "francia"),
            ("grande", "más grande", "pequeño", "más pequeño")
        ]
        correct = 0
        for a, b, c, d in analogies:
            result = model.get_analogies(a, b, c)
            if d in [word for word, _ in result]:
                correct += 1
        return correct / len(analogies)

    def evaluate_word_similarity(self, model):
        rg65_spanish_pairs = [
            ("coche", "automóvil", 0.98),
            ("viaje", "vuelo", 0.36),
            ("hotel", "reservación", 0.41),
            ("comida", "fruta", 0.23),
            ("tren", "coche", 0.13)
        ]
        model_similarities = []
        human_similarities = []
        for word1, word2, human_score in rg65_spanish_pairs:
            vec1 = model.get_word_vector(word1)
            vec2 = model.get_word_vector(word2)
            model_similarity = cosine_similarity([vec1], [vec2])[0][0]
            model_similarities.append(model_similarity)
            human_similarities.append(human_score)
        correlation, _ = spearmanr(model_similarities, human_similarities)
        return correlation

def main(model_path, get_preprocessed_texts_func, config_path):
    trainer = FastTextTrainer(model_path, get_preprocessed_texts_func, config_path)
    model = trainer.load_or_train_model()
    logger.info(f"FastText model loaded/trained successfully. Model path: {model_path}")
    return model

if __name__ == "__main__":
    # This block will only be executed if the script is run directly
    # You'll need to implement get_preprocessed_texts_func and set the paths
    from dotenv import load_dotenv
    load_dotenv()

    model_path = os.getenv("FASTTEXT_MODEL_PATH")
    config_path = os.getenv("FASTTEXT_CONFIG_PATH")

    # You'll need to implement this function or import it from your data ingestion service
    def get_preprocessed_texts():
        # Implement your text preprocessing logic here
        pass

    main(model_path, get_preprocessed_texts, config_path)