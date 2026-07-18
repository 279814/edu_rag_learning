import configparser
import os

current_filepath = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_filepath))
config_file = os.path.join(project_root, 'config.ini')

class Config():
    def __init__(self, config_file=config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

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

if __name__ == '__main__':
    config = Config()
    print(config_file)
    print(config.MYSQL_HOST)
    print(config.MYSQL_PORT)
    print(config.MYSQL_USER)
    print(config.MYSQL_PASSWORD)
    print(config.MYSQL_DATABASE)

    print(config.REDIS_HOST)
    print(config.REDIS_PORT)
    print(config.REDIS_PASSWORD)
    print(config.REDIS_DB)

    print(config.LOG_FILE)
