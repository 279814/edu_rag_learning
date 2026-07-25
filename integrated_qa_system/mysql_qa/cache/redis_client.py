# cache/redis_client.py
# 导入 Redis 客户端
import redis
# 导入 JSON 处理
import json

import os, sys
current_filepath = os.path.abspath(__file__)
model_path = os.path.dirname(os.path.dirname(current_filepath))
project_root = os.path.dirname(model_path)
sys.path.insert(0, project_root)

# 导入配置和日志
from base import Config, logger


class RedisClient:
    def __init__(self):
        # 初始化日志
        self.logger = logger
        try:
            # 连接 Redis
            self.client = redis.StrictRedis(
                host=Config().REDIS_HOST,
                port=Config().REDIS_PORT,
                password=Config().REDIS_PASSWORD,
                db=Config().REDIS_DB,
                decode_responses=True
            )
            # 记录连接成功
            self.logger.info("Redis 连接成功")
        except redis.RedisError as e:
            # 记录连接失败
            self.logger.error(f"Redis 连接失败: {e}")
            raise

    def set_data(self, key, value, expire=None):
        # 存储数据到 Redis（expire: 过期秒数，None 表示永不过期）
        try:
            # 存储 JSON 数据
            self.client.set(key, json.dumps(value), ex=expire)
            # 记录存储成功
            self.logger.info(f"存储数据到 Redis: {key} (过期: {expire if expire else '永不'})")
        except redis.RedisError as e:
            # 记录存储失败
            self.logger.error(f"Redis 存储失败: {e}")

    def get_data(self, key):
        # 从 Redis 获取数据
        try:
            # 获取数据
            data = self.client.get(key)
            # 返回解析后的 JSON 数据或 None
            return json.loads(data) if data else None
        except redis.RedisError as e:
            # 记录获取失败
            self.logger.error(f"Redis 获取失败: {e}")
            # 返回 None
            return None

    def get_answer(self, query):
        # 获取查询的缓存答案
        try:
            # 从 Redis 获取答案
            answer = self.client.get(f"answer:{query}")
            if answer:
                # 记录获取成功
                self.logger.info(f"从 Redis 获取答案: {query}")
                # 返回答案
                return json.loads(answer)
            # 返回 None
            return None
        except redis.RedisError as e:
            # 记录查询失败
            self.logger.error(f"Redis 查询失败: {e}")
            # 返回 None
            return None
if __name__ == '__main__':
    redcli = RedisClient()
    print(redcli)
