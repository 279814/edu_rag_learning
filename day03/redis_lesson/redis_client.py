import redis
import json
from base import Config, logger


class RedisClient:
    def __init__(self):
        self.logger = logger
        try:
            self.client = redis.StrictRedis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                password=Config.REDIS_PASSWORD,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            self.logger.info("Redis连接成功")
        except redis.RedisError as e:
            self.logger.error(f'Redis连接失败: {e}')
            raise

    def set_data(self, key, value):
        try:
            self.client.set(key, json.dumps(value))
            self.logger.info(f'Redis存储数据成功: {key}: {value}')
        except redis.RedisError as e:
            self.logger.error(f'Redis存储数据失败: {e}')

    def get_data(self, key):
        try:
            result = self.client.get(key)
            return json.loads(result) if result else None
        except redis.RedisError as e:
            self.logger.error(f'Redis获取数据失败: {e}')
            return None

    def get_answer(self, query):
        try:
            answer = self.client.get(f'answer:{query}')
            return json.loads(answer) if answer else None
        except redis.RedisError as e:
            self.logger.error(f'Redis获取答案失败: {e}')
            return None

if __name__ == '__main__':
    client = RedisClient()
    client.set_data('user', {'name': 'TOM', 'age': 19})
    client.set_data('answer:黑马程序员', "黑马程序员...")
    print(client.get_data('user'))
    print(client.get_answer('黑马程序员'))