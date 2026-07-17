import logging
import os


abspath = os.path.abspath(__file__)
# print(abspath)
dirname = os.path.dirname(os.path.dirname(abspath))
# print(dirname)
log_file = os.path.join(dirname, r'logs/app.log')
# print(log_file)

def setup_logger(name: str, log_file=log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(filename=log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(level=logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

if __name__ == '__main__':
    setup_logger('MainAPP')