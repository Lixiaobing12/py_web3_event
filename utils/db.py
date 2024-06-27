import pymysql
import os


def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
    )
    return connection
