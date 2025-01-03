from typing import List,Dict,Any
import pymysql as sql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from enum import Enum
class DataType(Enum):
    pass
class Sqldb():
    def __init__(self):
        self.conn=sql.connect(host='localhost',user='litterpigger',passwd='lhb1999114',port=3306)
        self.db_init()
    @contextmanager
    def db_cursor(self,db_name:str='crypto',table_name:str=None):
        cursor=self.conn.cursor(DictCursor)
        if db_name is not None:
            cursor.execute(
            f'USE {db_name}'
            )
        yield cursor
        self.conn.commit()
        cursor.close()
    def db_dropper(self,db_name='crypto'):
        with self.db_cursor(db_name=None) as cursor:
            cursor.execute(f'DROP DATABASE {db_name}')
            print(f'DATABASE {db_name} has been dropped')
    def db_init(self):
        with self.db_cursor() as cursor:
            cursor.execute("""
                   CREATE DATABASE IF NOT EXISTS crypto
                   """)
    def show_all_db(self):
        with self.db_cursor('crypto') as cursor:
            cursor.execute("""
            SHOW DATABASES
            """
            )
            result=cursor.fetchall()
            print(result)
    def table_creator(
        self,
        table_name:str,
        primary_key:Dict[str,List[Dict[str,Any]]],
        attribute:List[Dict[str,Any]]
        ):
            pass

db=Sqldb() 
db.db_dropper()
