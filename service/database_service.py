import pyodbc
from typing import List, Dict, Union,Tuple

import config as con



class Database:

    def __init__(self,driver='{SQL Server}'):
        self.server = con.SERVER
        self.database = con.DATABASE
        self.driver = driver
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
         if self.conn is None:
            conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes'
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()

    
    def insert_chat(self,userid:int ,role: str, content: str ) -> None:
        if self.conn is None:
            self.connect()
        try:
            query = "INSERT INTO ChatHistory (userid,role, content) VALUES (?, ?, ?)"
            self.cursor.execute(query, (userid, role, content))
            self.conn.commit()
            print("Chat inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Union[str, int, float]]]:
        
        if self.conn is None:
            self.connect()
        try:
            self.cursor.execute(query, params)  
            rows = self.cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip([column[0] for column in self.cursor.description], row)))
            
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return []