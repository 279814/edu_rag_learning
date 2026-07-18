import logging
import os
from config import Config

config = Config()
LOG_FILE = config.LOG_FILE
def setup_logging():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    logger = logging.getLogger('EduRAG')
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not logger.handlers:
        # 创建文件处理器
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        # 设置文件处理器级别
        file_handler.setLevel(logging.INFO)
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        # 设置控制台处理器级别
        console_handler.setLevel(logging.INFO)
        # 为文件处理器设置格式
        file_handler.setFormatter(formatter)
        # 为控制台处理器设置格式
        console_handler.setFormatter(formatter)
        # 添加文件处理器
        logger.addHandler(file_handler)
        # 添加控制台处理器
        logger.addHandler(console_handler)
        # 返回日志器
    return logger

# 初始化日志器
logger = setup_logging()

if __name__ == '__main__':
    # logger = setup_logging()
    # logger.info('test')
    print(config.LOG_FILE)