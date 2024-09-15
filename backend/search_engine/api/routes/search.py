import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from search_engine.search.search_service import SearchService
from search_engine.embeddings.fasttext_embedding import FastTextEmbedding
from search_engine.embeddings.transformer_embedding import TransformerEmbedding
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()


embedding_type = os.getenv("EMBEDDING_TYPE")
config_file_path = os.getenv("CONFIG_FILE_PATH")

with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

if embedding_type == "fasttext":
    embedding_model = FastTextEmbedding(config=config)
elif embedding_type == "transformer":
    embedding_model = TransformerEmbedding(config=config)
else:
    raise ValueError(f"Unsupported embedding type: {embedding_type}")

# Instantiate the search service with the embedding model
search_service = SearchService(embedding=embedding_model)



@router.get("/search")
async def semantic_search(
    query: str,
    category: str = None,
    limit: int = 5,
    threshold: float = None
):
    try:
        logger.info(f"Received search request - query: {query}, category: {category}, limit: {limit}, threshold: {threshold}")
        results = search_service.search(query, category, limit, threshold)
        logger.info(f"Search completed, found {len(results)} results")
        response = [
            {
                "id": str(r['id']),
                "score": r['score'],
                "pregunta": str(r.get("pregunta", "")),
                "respuesta": str(r.get("respuesta", "")),
                "grupo": str(r.get("grupo", "")),
                "tema": str(r.get("tema", "") or "")
            } for r in results
        ]
        return response
    except Exception as e:
        logger.error(f"Error in semantic_search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during the search process")

@router.get("/article/{article_id}")
async def get_article(article_id: str):
    try:
        logger.info(f"Received request for article with id: {article_id}")
        article = search_service.get_article(article_id)
        if article:
            logger.info(f"Article found: {article['id']}")
            return article
        logger.warning(f"Article not found: {article_id}")
        raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        logger.error(f"Error in get_article: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the article")

@router.get("/categories")
async def get_categories():
    try:
        logger.info("Received request for categories")
        categories = search_service.get_categories()
        logger.info(f"Retrieved {len(categories)} categories")
        return categories
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while retrieving categories")