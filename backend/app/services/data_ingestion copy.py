import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
from ..utils import extract_text_from_html  # Import the utility function

class DataIngestionService:
    def __init__(self, path="./vector_db_5"):
        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.client = QdrantClient(path=self.path)
        self.collection_name = 'articles'
        self.ensure_collection()

    def ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection_name for collection in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE)
            )

    def ingest_data(self, file_path: str):
        df = pd.read_excel(file_path)
        total_rows = len(df)
        
        points = []
        for index, row in tqdm(df.iterrows(), total=total_rows):
            pregunta_html = str(row['pregunta'])
            respuesta_html = str(row['respuesta'])
            
            # Extract text from HTML
            pregunta_text = extract_text_from_html(pregunta_html)
            respuesta_text = extract_text_from_html(respuesta_html)
            
            # Debugging statements
            # print(f"Index: {index}, Pregunta: {pregunta_text}, Respuesta: {respuesta_text}")
            
            text = pregunta_text + ' ' + respuesta_text
            embedding = self.model.encode([text])[0].tolist()
            
            # Debugging statement
            # print(f"Index: {index}, Embedding: {embedding}")
            
            point = models.PointStruct(
                id=int(row['id']),
                payload={
                    "pregunta": pregunta_text,
                    "respuesta": respuesta_html,
                    "grupo": row['grupo'],
                    "tema": row['tema']
                },
                vector=embedding
            )

            points.append(point)

            if (index + 1) % 100 == 0 or index == total_rows - 1:
                # Debugging statement before upsert
                # print(f"Upserting points: {points}")
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                points = []
                print(f"Processed {index + 1}/{total_rows} articles")

        print("Data ingestion completed.")

    def retrieve_data(self):
        # Retrieve data from the vector database
        retrieved_points = self.client.retrieve(
            collection_name=self.collection_name,
            filter=models.Filter(
                must=[
                    models.Condition(
                        key="grupo",
                        match=models.MatchValue(value=0)
                    )
                ]
            )
        )

        # Print the retrieved data
        for point in retrieved_points:
            print(f"ID: {point.id}, Pregunta: {point.payload['pregunta']}, Respuesta: {point.payload['respuesta']}, Grupo: {point.payload['grupo']}, Tema: {point.payload['tema']}")