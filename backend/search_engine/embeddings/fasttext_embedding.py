import os
import fasttext
import numpy as np
from typing import List, Dict
from tqdm import tqdm
from .base_embedding import BaseEmbedding

class FastTextEmbedding(BaseEmbedding):
    def __init__(self, config, training_data=None):
        self.config = config
        self.training_data = training_data
        self.model = self.load_or_train_model()

    @property
    def vector_size(self) -> int:
        return self.model.get_dimension()

    def load_or_train_model(self):
        model_path = self.config.get('model_path')
        if model_path is not None:
            return self.load_model(model_path)
        elif self.training_data:
            self.model=self.train(self.training_data)
            self.model.save_model("fasttext_model.bin")
            return self.model
        else:
            raise ValueError("No model path or training data provided")

    def train(self, texts: List[str]):
        # Prepare training data
        with open("temp_training_data.txt", "w", encoding="utf-8") as f:
            for text in texts:
                f.write(f"{text['text']}\n")

        # Train the model
        model = fasttext.train_unsupervised(
            "temp_training_data.txt",
            model=self.config.get('model', 'skipgram'),
            dim=self.config.get('dim', 100),
            lr=self.config.get('lr', 0.05),
            epoch=self.config.get('epoch', 5),
            wordNgrams=self.config.get('wordNgrams', 1),
            minn=self.config.get('minn', 3),
            maxn=self.config.get('maxn', 6),
            thread=self.config.get('thread', 4)
        )

        # Remove temporary file
        import os
        os.remove("temp_training_data.txt")

        return model

    def load_model(self, model_path: str):
        return fasttext.load_model(model_path)

    def save_model(self, model_path: str):
        self.model.save_model(model_path)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in tqdm(texts)]

    def embed_query(self, text: str) -> List[float]:
        return self.model.get_sentence_vector(text).tolist()

    def get_embeddings_with_data(self) -> List[Dict]:
        if self.training_data is None:
            raise ValueError("No training data available")
        
        embeddings_with_data = []
        for i, text in enumerate(tqdm(self.training_data, desc="Generating embeddings")):
            embedding = self.embed_query(text['text'])
            embeddings_with_data.append({
                'id': str(i),
                'text': text['text'],
                'embedding': embedding,
                'pregunta': text['pregunta'],
                'respuesta': text['respuesta'],
                'grupo': text['grupo']

            })
        return embeddings_with_data