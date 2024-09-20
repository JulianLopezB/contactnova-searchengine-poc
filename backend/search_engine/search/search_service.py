import os
import logging
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..embeddings.base_embedding import BaseEmbedding

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, embedding: BaseEmbedding):
        self.embedding = embedding
        self.qdrant_path = os.getenv("VECTOR_DB_PATH")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME")
        self.default_search_limit = int(os.getenv("SEARCH_LIMIT", 15))
        self.default_search_threshold = float(os.getenv("SEARCH_THRESHOLD", 0.0))
        self.hnsw_ef = int(os.getenv("HNSW_EF", 128))
        
        self.client = QdrantClient(path=self.qdrant_path)

    def search(self, query: str, category: str = None, limit: int = None, threshold: float = None) -> List[Dict]:
        query_vector = self.embedding.embed_query(query)
        
        # Use default values if not provided
        limit = limit if limit is not None else self.default_search_limit
        threshold = threshold if threshold is not None else self.default_search_threshold

        filter_conditions = []
        if category:
            filter_conditions.append(
                models.FieldCondition(key="grupo", match=models.MatchValue(value=int(category)))
            )
            
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=models.Filter(must=filter_conditions) if filter_conditions else None,
            limit=limit * 2,  # Increase the limit to account for filtering
            score_threshold=threshold,
            # search_params=models.SearchParams(hnsw_ef=self.hnsw_ef),
            search_params=models.SearchParams(hnsw_ef=32),
        )
        
        results = [
            {
                "id": result.id,
                "score": result.score,
                "pregunta": result.payload.get('pregunta'),
                "respuesta": result.payload.get('respuesta'),
                "grupo": result.payload.get('grupo'),

            }
            for result in search_result[:limit]
        ]

        logger.info(f"Search completed, found {len(search_result)} results, returning {len(results)}")
        return results

    def get_categories(self):
        logger.info("Fetching categories")
        result = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(),
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        categories = set()
        for point in result[0]:
            category = point.payload.get("grupo")
            if category:
                categories.add(category)
        
        logger.info(f"Retrieved {len(categories)} categories")
        return sorted(list(categories))

    def get_article(self, article_id: str) -> Optional[Dict]:
        try:
            result = self.client.retrieve(collection_name=self.collection_name,ids=[str(article_id)],with_payload=True,with_vectors=False)
            
            if result:
                article = result[0]
                return {
                    "id": str(article.id),
                    "pregunta": str(article.payload.get("pregunta", "")),
                    "grupo": str(article.payload.get("grupo", "")),
                    "tema": str(article.payload.get("tema", "") or ""),
                    "respuesta": str(article.payload.get("respuesta", "")).replace("_x000d_", "")
                }
            else:
                logger.warning(f"Article not found: {article_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving article {article_id}: {str(e)}")
            return None