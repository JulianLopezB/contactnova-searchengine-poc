import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.models import Filter, FieldCondition, MatchValue
import fasttext
import numpy as np

load_dotenv()

class SearchService:
    def __init__(self):
        self.client = QdrantClient(path=os.getenv("VECTOR_DB_PATH"))
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME")
        self.fasttext_model = fasttext.load_model(os.getenv("FASTTEXT_MODEL_PATH"))

    def search(self, query: str, category: str = None, limit: int = int(os.getenv("SEARCH_LIMIT", 5))):
        filter_conditions = []
        if category:
            filter_conditions.append(
                FieldCondition(key="grupo", match=MatchValue(value=int(category)))
            )
        query_vector = self._get_embedding(query)
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=Filter(must=filter_conditions) if filter_conditions else None,
            limit=limit,
            search_params=models.SearchParams(hnsw_ef=int(os.getenv("HNSW_EF", 128)), exact=False),
        )
        return search_result

    def get_article(self, article_id: int):
        search_result = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[article_id]
        )
        return search_result[0] if search_result else None

    def get_categories(self):
        groups = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(),
            limit=int(os.getenv("CATEGORY_SCROLL_LIMIT", 10000)),
            with_payload=["grupo"],
            with_vectors=False
        )[0]
        
        unique_groups = set(point.payload["grupo"] for point in groups if "grupo" in point.payload)
        return sorted(list(unique_groups))

    def _get_embedding(self, text: str):
        return self.fasttext_model.get_sentence_vector(text)