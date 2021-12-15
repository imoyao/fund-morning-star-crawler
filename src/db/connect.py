
import os

import pymysql
from dotenv import load_dotenv


def connect():
    load_dotenv()
    env_db_host = os.getenv('db_host')
    env_db_name = os.getenv('db_name')
    env_db_user = os.getenv('db_user')
    env_db_password = os.getenv('db_password')
    env_db_port = int(os.getenv('db_port'))
    connect = pymysql.connect(
        host=env_db_host, user=env_db_user, password=env_db_password, db=env_db_name, port=env_db_port,charset='utf8')
    return connect

def connect_dict():
    load_dotenv()
    env_db_host = os.getenv('db_host')
    env_db_name = os.getenv('db_stock_name')
    env_db_user = os.getenv('db_user')
    env_db_password = os.getenv('db_password')
    env_db_port = os.getenv('prot')
    connect = pymysql.connect(
        host=env_db_host, user=env_db_user, password=env_db_password, db=env_db_name, port=env_db_port,charset='utf8')
    connect_dict = {
        'connect': connect,
        'cursor': connect.cursor(),
        'dict_cursor': connect.cursor(pymysql.cursors.DictCursor)
    }
    return connect_dict


if __name__ == '__main__':
    connect()
