import jieba, os, sys

current_filepath = os.path.abspath(__file__)
model_path = os.path.dirname(os.path.dirname(current_filepath))
project_root = os.path.dirname(model_path)
sys.path.insert(0, project_root)

from base import logger


def preprocess_text(text):
    try:
        logger.info('开始预处理文本')
        return jieba.lcut(text.lower())
    except Exception as e:
        logger.error(f'文本预处理失败: {e}')
        return []

