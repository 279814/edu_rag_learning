from redis_client import RedisClient
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 初始化 Redis 客户端
    redis_client = RedisClient()
    # 示例数据
    key = "user:1"
    value = {"name": "Alice", "age": 25}
    # 存储数据
    redis_client.set_data(key, value)
    # 获取数据
    result = redis_client.get_data(key)
    if result:
        logger.info(f"查询结果: {result}")
    else:
        logger.info("未找到数据")
    # 示例查询缓存
    query = "test_query"
    answer = redis_client.get_answer(query)
    if answer:
        logger.info(f"缓存答案: {answer}")
    else:
        logger.info("未找到缓存答案")

if __name__ == "__main__":
    main()
