import sys
import os

# print('-'*22)
# for path in sys.path:
#     print(path)
current_filepath = os.path.abspath(__file__)
model_path = os.path.dirname(current_filepath)
project_root = os.path.dirname(model_path)
sys.path.insert(0, project_root)
sys.path.insert(0, model_path)
# print('-'*212)
# for path in sys.path:
#     print(path)

from config import Config
from logger import logger

