import pandas as pd
import numpy as np
import logging
from typing import List, Tuple, Dict
from tqdm import tqdm
from ..embeddings.base_embedding import BaseEmbedding
from .metrics import evaluate_rankings
from ..utils.data_preprocessor import DataPreprocessor

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self, embedding: BaseEmbedding):
        self.embedding = embedding

    def load_articles_and_rankings(self, articles_file: str, rankings_file: str) -> Tuple[Dict[int, str], List[Dict]]:
        logger.info(f"Loading and preprocessing articles from {articles_file}")
        preprocessor = DataPreprocessor(articles_file)
        df = preprocessor._load_and_filter_data()
        all_articles = {row['id']: preprocessor._process_row(row) for _, row in df.iterrows()}
        logger.info(f"Loaded {len(all_articles)} articles")

        logger.info(f"Loading rankings from {rankings_file}")
        with open(rankings_file, 'r', encoding='utf-8') as f:
            content = f.read()

        queries = content.split('### Consulta')[1:]  # Split by queries, ignore the first empty part
        rankings = []
        relevant_article_ids = set()

        for query in queries:
            lines = query.strip().split('\n')
            query_id = int(lines[0].split(':')[0].strip())
            query_text = lines[1].split('**Consulta:**')[1].strip()
            article_ranking = [int(line.split('.')[1].strip()) for line in lines[3:8]]  # Get the article IDs
            relevant_article_ids.update(article_ranking)

            rankings.append({
                'query_id': query_id,
                'query_text': query_text,
                'articles_ranking': article_ranking
            })

        logger.info(f"Loaded {len(rankings)} queries with rankings")
        relevant_articles = {article_id: all_articles[article_id] for article_id in relevant_article_ids}
        logger.info(f"Identified {len(relevant_articles)} relevant articles for evaluation")
        return relevant_articles, rankings

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def evaluate(self, articles_file: str, rankings_file: str) -> dict:
        logger.info("Starting evaluation")
        articles, rankings = self.load_articles_and_rankings(articles_file, rankings_file)
        
        logger.info("Computing article embeddings")
<<<<<<< HEAD
        article_embeddings = {article_id: self.embedding.embed_query(text['text']) for article_id, text in tqdm(articles.items(), desc="Embedding articles")}
=======
        article_embeddings = {article_id: self.embedding.embed_query(article['text']) for article_id, article in tqdm(articles.items(), desc="Embedding articles")}
>>>>>>> da19aff732119a342b591889221d328c265d69ab

        predictions = []
        ground_truth = []

        logger.info("Computing rankings for queries")
        for i, query in enumerate(tqdm(rankings, desc="Processing queries")):
            query_text = query['query_text']
            query_embedding = self.embedding.embed_query(query_text)
            
            scores = {article_id: self.cosine_similarity(query_embedding, article_embedding) 
                      for article_id, article_embedding in article_embeddings.items()}
            
            ranked_articles = sorted(scores, key=scores.get, reverse=True)
            predictions.append(ranked_articles[:5])
            ground_truth.append(query['articles_ranking'])

            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i+1}/{len(rankings)} queries")

        logger.info("Computing evaluation metrics")
        results = evaluate_rankings(predictions, ground_truth)
        logger.info("Evaluation completed")
        return results