import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import pandas as pd
from tqdm import tqdm
import re
from bs4 import BeautifulSoup
import fasttext
import numpy as np

load_dotenv()

class DataIngestionService:
    def __init__(self):
        self.path = os.getenv("VECTOR_DB_PATH")
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.client = QdrantClient(path=self.path)
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME")
        self.ensure_collection()
        self.fasttext_model = None

    def ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=300, distance=models.Distance.COSINE)
            )

    def preprocess_text(self, html_content):
        # Remove HTML tags
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # Remove special characters but keep some punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
        
        # Convert to lowercase and remove extra whitespace
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def train_fasttext(self, texts):
        # Prepare data for FastText
        with open('temp_training_data.txt', 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(f"{text}\n")
        
        # Train FastText model with improved parameters
        self.fasttext_model = fasttext.train_unsupervised(
            'temp_training_data.txt',
            model='skipgram',
            dim=300,
            epoch=int(os.getenv("FASTTEXT_EPOCH", "50")),
            lr=float(os.getenv("FASTTEXT_LR", "0.05")),
            wordNgrams=int(os.getenv("FASTTEXT_WORD_NGRAMS", "2")),
            minn=int(os.getenv("FASTTEXT_MINN", "2")),
            maxn=int(os.getenv("FASTTEXT_MAXN", "5")),
            thread=int(os.getenv("FASTTEXT_THREAD", "4"))
        )
        
        # Save the trained model
        self.fasttext_model.save_model(os.getenv("FASTTEXT_MODEL_PATH"))
        
        # Remove temporary file
        os.remove('temp_training_data.txt')

    def get_embedding(self, text):
        if self.fasttext_model is None:
            raise ValueError("FastText model not trained. Call train_fasttext first.")
        return self.fasttext_model.get_sentence_vector(text)

    def ingest_data(self, file_path: str):
        df = pd.read_excel(file_path)
        total_rows = len(df)
        
        preprocessed_texts = []
        points = []

        for index, row in tqdm(df.iterrows(), total=total_rows):
            pregunta_html = str(row['pregunta'])
            respuesta_html = str(row['respuesta'])
            
            pregunta_text = self.preprocess_text(pregunta_html)
            respuesta_text = self.preprocess_text(respuesta_html)
            
            full_text = pregunta_text + ' ' + respuesta_text
            preprocessed_texts.append(full_text)
            
            points.append({
                'id': int(row['id']),
                'pregunta': pregunta_text,
                'respuesta': respuesta_html,
                'grupo': row['grupo'],
                'tema': row['tema'],
                'text': full_text
            })

        # Train FastText model
        print("Training FastText model...")
        self.train_fasttext(preprocessed_texts)

        # Generate embeddings and upsert to Qdrant
        batch_size = int(os.getenv("UPSERT_BATCH_SIZE", "100"))
        for i in tqdm(range(0, len(points), batch_size), desc="Generating embeddings and upserting"):
            batch = points[i:i+batch_size]
            batch_points = []
            for point in batch:
                embedding = self.get_embedding(point['text'])
                
                batch_points.append(models.PointStruct(
                    id=point['id'],
                    payload={
                        "pregunta": point['pregunta'],
                        "respuesta": point['respuesta'],
                        "grupo": point['grupo'],
                        "tema": point['tema']
                    },
                    vector=embedding.tolist()
                ))
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch_points
            )

        print("Data ingestion completed.")