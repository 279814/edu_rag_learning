import jieba
from rank_bm25 import BM25L
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)
class BM25Search:
    def __init__(self, documents):
        self.documents = documents
        self.tokenized_docs = [jieba.lcut(doc) for doc in documents]
        self.bm25 = BM25L(self.tokenized_docs)
        logger.info("BM25初始化完成")

    def search(self, query: str):
        try:
            tokenized_query = jieba.lcut(query)
            scores = self.bm25.get_scores(tokenized_query)
            logger.info(f"查询: {query}, 得分: {scores}")
            best_idx = scores.argmax()
            best_score = scores[best_idx]
            best_doc = self.documents[best_idx]
            logger.info(f"查询: {query}, 文档: {best_doc}, 分数: {best_score}")
            return best_doc, best_score
        except Exception as e:
            logger.error(f"查询: {query}, 错误: {e}")
            return None, 0
