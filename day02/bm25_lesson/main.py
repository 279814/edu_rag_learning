from retrieval.bm25_search import BM25Search
import logging
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 示例文档集合
    documents = ["我喜欢编程", "编程很有趣"]
    # 初始化BM25检索器
    bm25_search = BM25Search(documents)
    # 示例查询
    query = "他喜欢编程"
    # 执行检索
    result, score = bm25_search.search(query)
    if result:
        logger.info(f"查询结果: {result}, 得分: {score}")
    else:
        logger.info("未找到匹配结果")

if __name__ == "__main__":
    main()