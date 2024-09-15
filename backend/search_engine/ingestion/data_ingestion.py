import os
import logging
from typing import List, Dict
import uuid
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..embeddings.base_embedding import BaseEmbedding

logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self, embedding: BaseEmbedding):
        self.embedding = embedding
        self.qdrant_path = os.getenv("VECTOR_DB_PATH")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME")
        
        if not os.path.exists(self.qdrant_path):
            os.makedirs(self.qdrant_path)
        
        self.client = QdrantClient(path=self.qdrant_path)
        self.recreate_collection()

    def recreate_collection(self):
        # Delete the collection if it exists
        collections = self.client.get_collections().collections
        if any(collection.name == self.collection_name for collection in collections):
            logger.info(f"Deleting existing collection: {self.collection_name}")
            self.client.delete_collection(collection_name=self.collection_name)

        # Create a new collection
        logger.info(f"Creating new collection: {self.collection_name}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=self.embedding.vector_size, distance=models.Distance.COSINE),
        )

    def ingest_data(self):
        logger.info("Starting data ingestion")
        
        data_with_embeddings = self.embedding.get_embeddings_with_data()
        logger.info(f"Loaded and embedded {len(data_with_embeddings)} records")
        
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),  # Generate a new UUID for each point
                vector=item['embedding'],
                payload={k: v for k, v in item.items() if k != 'embedding'}
            )
            for item in data_with_embeddings
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Ingested {len(points)} points into Qdrant collection '{self.collection_name}'")
