from fastapi import APIRouter
from app.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()

@router.get("/search")
def semantic_search(query: str, category: str = None, limit: int = 5):
    results = search_service.search(query, category, limit)

    response = [
        {
            "id": r.id,
            "pregunta": str(r.payload.get("pregunta", "")),
            "grupo": str(r.payload.get("grupo", "")),
            "tema": str(r.payload.get("tema", "") or "")
        } for r in results
    ]

    return response

@router.get("/article/{article_id}")
def get_article(article_id: int):
    article = search_service.get_article(article_id)
    if article:
        return {
            "id": article.id,
            "pregunta": str(article.payload.get("pregunta", "")),
            "grupo": str(article.payload.get("grupo", "")),
            "tema": str(article.payload.get("tema", "") or ""),
            "respuesta": str(article.payload.get("respuesta", ""))
        }
    return {"error": "Article not found"}

@router.get("/categories")
def get_categories():
    categories = search_service.get_categories()
    return categories