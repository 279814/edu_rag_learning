import configparser
import os

current_filepath = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_filepath))
config_file = os.path.join(project_root, 'config.ini')

class Config():
    def __init__(self, config_file=config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

        self.MYSQL_HOST = self.config.get('mysql', 'host', fallback='localhost')
        self.MYSQL_PORT = self.config.get('mysql', 'port', fallback='3306')
        self.MYSQL_USER = self.config.get('mysql', 'user', fallback='root')
        self.MYSQL_PASSWORD = self.config.get('mysql', 'password', fallback='password')
        self.MYSQL_DATABASE = self.config.get('mysql', 'database', fallback='mysql')

        self.REDIS_HOST = self.config.get('redis', 'host', fallback='localhost')
        self.REDIS_PORT = self.config.get('redis', 'port', fallback='6379')
        self.REDIS_PASSWORD = self.config.get('redis', 'password', fallback='password')
        self.REDIS_DB = self.config.get('redis', 'db', fallback='0')

        self.LOG_FILE = self.config.get('logger', 'log_file', fallback='log.txt')

        current_filepath = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_filepath))
        self.LOG_FILE = os.path.join(project_root, self.LOG_FILE)

        # Milvus 配置
        # Milvus 主机地址
        self.MILVUS_HOST = self.config.get('milvus', 'host', fallback='localhost')
        # Milvus 端口
        self.MILVUS_PORT = self.config.get('milvus', 'port', fallback='19530')
        self.MILVUS_USER = self.config.get('milvus', 'user', fallback='root')
        self.MILVUS_PASSWORD = self.config.get('milvus', 'password', fallback='password')
        # Milvus 数据库名
        self.MILVUS_DATABASE_NAME = self.config.get('milvus', 'database_name', fallback='itcast')
        # Milvus 集合名
        self.MILVUS_COLLECTION_NAME = self.config.get('milvus', 'collection_name', fallback='edurag_final')

        # LLM 配置
        # LLM 模型名
        self.LLM_MODEL = self.config.get('llm', 'model', fallback='qwen-plus')
        self.EMBEDDING_MODEL = self.config.get('llm', 'embedding_model', fallback='qwen-plus')
        # DashScope API 密钥
        self.DASHSCOPE_API_KEY = self.config.get('llm', 'dashscope_api_key')
        # DashScope API 地址
        self.DASHSCOPE_BASE_URL = self.config.get('llm', 'dashscope_base_url',
                                                  fallback='https://dashscope.aliyuncs.com/compatible-mode/v1')

        # 检索参数
        # 父块大小
        self.PARENT_CHUNK_SIZE = self.config.getint('retrieval', 'parent_chunk_size', fallback=1200)
        # 子块大小
        self.CHILD_CHUNK_SIZE = self.config.getint('retrieval', 'child_chunk_size', fallback=300)
        # 块重叠大小
        self.CHUNK_OVERLAP = self.config.getint('retrieval', 'chunk_overlap', fallback=50)
        # 检索返回数量
        self.RETRIEVAL_K = self.config.getint('retrieval', 'retrieval_k', fallback=5)
        # 最终候选数量
        self.CANDIDATE_M = self.config.getint('retrieval', 'candidate_m', fallback=2)

        #应用配置
        self.CUSTOMER_SERVICE_PHONE = self.config.get('app', 'customer_service_phone')
        self.VALID_SOURCES = eval(self.config.get('app', 'valid_sources'))

if __name__ == '__main__':
    config = Config()
    # print(config_file)
    # print(config.MYSQL_HOST)
    # print(config.MYSQL_PORT)
    # print(config.MYSQL_USER)
    # print(config.MYSQL_PASSWORD)
    # print(config.MYSQL_DATABASE)
    #
    # print(config.REDIS_HOST)
    # print(config.REDIS_PORT)
    # print(config.REDIS_PASSWORD)
    # print(config.REDIS_DB)
    #
    # print(config.LOG_FILE)

    # print(config.MILVUS_HOST)
    # print(config.MILVUS_PORT)
    # print(config.MILVUS_USER)
    # print(config.MILVUS_PASSWORD)
    # print(config.MILVUS_DATABASE_NAME)
    # print(config.MILVUS_COLLECTION_NAME)
    #
    # print(config.LLM_MODEL)
    # print(config.DASHSCOPE_API_KEY)
    # print(config.DASHSCOPE_BASE_URL)
    #
    # print(config.PARENT_CHUNK_SIZE)
    # print(config.CHILD_CHUNK_SIZE)
    # print(config.CHUNK_OVERLAP)
    # print(config.RETRIEVAL_K)
    # print(config.CANDIDATE_M)

    # print(config.CUSTOMER_SERVICE_PHONE)
    # print(config.VALID_SOURCES)
    print(config.EMBEDDING_MODEL)