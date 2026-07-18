from rank_bm25 import BM25Okapi
import numpy as np
import os, sys

current_filepath = os.path.abspath(__file__)
model_path = os.path.dirname(os.path.dirname(current_filepath))
sys.path.insert(0, model_path)
project_root = os.path.dirname(model_path)
sys.path.insert(0, project_root)

from base import logger
from cache import RedisClient
from db import MySQLClient
from utils import preprocess_text

class BM25Search:
    def __init__(self, redis_client, mysql_client):
        # 初始化日志
        self.logger = logger
        # 初始化 Redis 客户端
        self.redis_client = redis_client
        # 初始化 MySQL 客户端
        self.mysql_client = mysql_client
        # 初始化 BM25 模型
        self.bm25 = None
        # 初始化问题列表
        self.questions = None
        # 初始化原始问题
        self.original_questions = None
        # 加载数据
        self._load_data()

    def _load_data(self):
        # 加载数据
        original_key = "qa_original_questions"
        tokenized_key = "qa_tokenized_questions"
        self.original_questions = self.redis_client.get_data(original_key)
        tokenized_questions = self.redis_client.get_data(tokenized_key)
        if not self.original_questions or not tokenized_questions:
            # 从 MySQL 加载数据,并缓存redis
            self.original_questions = self.mysql_client.fetch_questions()
            if not self.original_questions:
                self.logger.error("从MySQL加载数据失败")
                return
            tokenized_questions = [preprocess_text(q[0]) for q in self.original_questions]
            # 缓存数据
            self.redis_client.set_data(original_key, [(q[0]) for q in self.original_questions])
            self.redis_client.set_data(tokenized_key, tokenized_questions)
            self.original_questions = [(q[0]) for q in self.original_questions]


        self.questions = tokenized_questions
        self.bm25 = BM25Okapi(self.questions)
        self.logger.info(f'BM25模型初始化完成')


    def _softmax(self, scores):
        exp_scores = np.exp(scores - np.max(scores))
        return exp_scores / exp_scores.sum()


    def search(self, query, threshold=0.85):
        #校验query
        if not query or not isinstance(query, str):
            self.logger.error(f"无效的查询: {query}")
            return None

        #查询缓存
        cached_answer = self.redis_client.get_answer(query)
        if cached_answer:
            self.logger.info(f"bm25搜索 从缓存中 获取答案: {query}")
            return cached_answer
        else:
            self.logger.info(f"bm25搜索 没有在缓存中 获取答案: {query}")

        #核心流程
        try:
            tokenized_query = preprocess_text(query)
            scores = self.bm25.get_scores(tokenized_query)
            softmax_scores = self._softmax(scores)
            best_idx = softmax_scores.argmax()
            best_score = softmax_scores[best_idx]
            if best_score >= threshold:
                original_question = self.original_questions[best_idx]
                answer = self.mysql_client.fetch_answer(original_question)
                if answer:
                    # 缓存答案
                    self.redis_client.set_data(f"answer:{query}", answer)
                    # 记录搜索成功
                    self.logger.info(f"搜索成功，Softmax 相似度: {best_score:.3f}")
                    # 返回答案和 False
                    return answer

            self.logger.info(f"未找到可靠答案，最高 Softmax 相似度: {best_score:.3f}")
            # 返回 None 和 True
            return None

        except Exception as e:
            # 记录搜索失败
            self.logger.error(f"搜索失败: {e}")
            # 返回 None
            return None



if __name__ == '__main__':
    redis_client = RedisClient()
    mysql_client = MySQLClient()

    bm25_search = BM25Search(redis_client=redis_client, mysql_client=mysql_client)
    # print(bm25_search.search(query='什么是AI'))
    print(bm25_search.search(query='redis 设置密码访问'))