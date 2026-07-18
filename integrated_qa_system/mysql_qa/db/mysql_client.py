import pymysql
import pandas as pd
import sys
import os

current_filepath = os.path.abspath(__file__)
model_path = os.path.dirname(os.path.dirname(current_filepath))
project_root = os.path.dirname(model_path)
sys.path.insert(0, project_root)

from base import Config, logger

class MySQLClient():
    def __init__(self):
        self.logger = logger
        try:
            self.connection = pymysql.connect(
                host=Config().MYSQL_HOST,
                port=int(Config().MYSQL_PORT),
                user=Config().MYSQL_USER,
                password=Config().MYSQL_PASSWORD,
                database=Config().MYSQL_DATABASE,
            )
            self.cursor = self.connection.cursor()
            self.logger.info("MySQL连接成功")
        except pymysql.MySQLError as e:
            self.logger.error(f"MySQL连接失败: {e}")
            raise

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS jpkb (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subject_name VARCHAR(20),
            question VARCHAR(1000),
            answer VARCHAR(1000))
        '''
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            self.logger.info("表创建成功")
        except pymysql.MySQLError as e:
            self.logger.error(f"表创建失败: {e}")
            raise

    def insert_data(self, csv_path):
        try:
            data = pd.read_csv(csv_path)
            for _, row in data.iterrows():
                insert_query = "INSERT INTO jpkb (subject_name, question, answer) VALUES (%s, %s, %s)"
                self.cursor.execute(insert_query, (row['学科名称'], row['问题'], row['答案']))
            self.connection.commit()
            self.logger.info("数据插入成功")
        except pymysql.MySQLError as e:
            self.logger.error(f"数据插入失败: {e}")
            self.connection.rollback()
            raise


    def fetch_questions(self):
        # 获取所有问题
        try:
            # 执行查询
            self.cursor.execute("SELECT question FROM jpkb")
            # 获取结果
            #   # results:(('static静态方法使用非静态变量',), ...)
            results = self.cursor.fetchall()
            # 记录获取成功
            self.logger.info("成功获取问题")
            # 返回结果
            return results
        except pymysql.MySQLError as e:
            # 记录查询失败
            self.logger.error(f"查询失败: {e}")
            # 返回空列表
            return []

    def fetch_answer(self, question):
        try:
            self.cursor.execute("SELECT answer FROM jpkb WHERE question = %s", (question,))
            result = self.cursor.fetchone()
            self.logger.info("mysql成功获取answer")
            return result[0] if result else None
        except pymysql.MySQLError as e:
            self.logger.error(f"mysql获取answer失败: {e}")
            return None

    def close(self):
        # 关闭数据库连接
        try:
            # 关闭连接
            self.connection.close()
            # 记录关闭成功
            self.logger.info("MySQL 连接已关闭")
        except pymysql.MySQLError as e:
            # 记录关闭失败
            self.logger.error(f"MySQL 关闭连接失败: {e}")

if __name__ == '__main__':
    mysql_client = MySQLClient()
    # mysql_client.create_table()
    # mysql_client.insert_data(csv_path='../data/JP学科知识问答.csv')
    # print(mysql_client.fetch_questions())
    # print(mysql_client.fetch_answer('用上下文管理器实现函数运行时间的计算?'))
    mysql_client.close()