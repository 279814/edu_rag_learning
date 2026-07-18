import os, sys
current_filepath = os.path.abspath(__file__)
model_path = os.path.dirname(os.path.dirname(current_filepath))
project_root = os.path.dirname(model_path)
sys.path.insert(0, project_root)

sys.path.insert(0, os.path.dirname(current_filepath))

from redis_client import RedisClient