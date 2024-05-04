import datetime
import os
from typing import Annotated, Dict, List, Optional, Tuple, Union

import config as con
import pyodbc
from dotenv import load_dotenv
from fastapi import Depends
from model import ChatRecord, MessageModel
from pyodbc import Row

load_dotenv()


class Database:
    def __init__(self) -> None:
        self.driver = os.getenv("DRIVER")
        self._connection_str = os.getenv("CONNECT_STRING")
        self.conn = None
        self.database = "ChatDatabase"
        self.cursor = None
        self._connect()

    def _connect(self) -> None:
        if self.conn is not None:
            return

        conn_str = f"DRIVER={self.driver};{self._connection_str}"
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

        if not self._database_and_table_exist():
            self._create_database_and_table()

    def _database_exists(self) -> bool:
        query = f"SELECT COUNT(*) FROM sys.databases WHERE name = '{self.database}'"
        self.cursor.execute(query)
        count = self.cursor.fetchone()[0]
        return count > 0

    def table_exists(self, table_name: str) -> bool:
        query = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'"
        self.cursor.execute(query)
        count = self.cursor.fetchone()[0]
        return count > 0

    def _database_and_table_exist(self) -> bool:
        database_exists = self._database_exists()
        table_exists = self.table_exists("ChatHistory")
        return database_exists and table_exists

    def _table_exists(self, table_name: str) -> bool:
        query = f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ? AND TABLE_SCHEMA = 'dbo'"
        self.cursor.execute(query, (table_name,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def _create_database_and_table(self) -> None:
        with open("./scripts/create_database.sql", "r") as file:
            sql_script = file.read()
        self.cursor.execute(sql_script)
        self.conn.commit()

    def insert(self, table: str, data: Dict) -> None:
        del data["id"]
        key_list = data.keys()
        value_list = [data.get(key) for key in key_list]
        query = f"INSERT INTO {table} ({','.join(key_list)}) VALUES ({', '.join(len(key_list)*['?'])});"
        self.cursor.execute(query, tuple(value_list))

    def get_by_id(self, table: str, id: str) -> Row:
        query = f"SELECT * FROM {table} WHERE id = ?;"
        self.cursor.execute(query, (id,))
        rows = self.cursor.fetchall()
        return rows[0]

    def get_all(self, table: str) -> List[Row]:
        query = f"SELECT * FROM {table}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def get_all_by(
        self,
        table: str,
        property_name: str,
        value: str | int,
        select_properties: Optional[List] = None,
        equal: bool = True,
    ) -> List[Row]:
        expression = "=" if equal else "!="
        select_property_names = (
            "*"
            if select_properties is None or len(select_properties) == 0
            else f"{', '.join(select_properties)}"
        )

        query = f"SELECT {select_property_names} FROM {table} WHERE {property_name} {expression} ?;"
        print(query)
        self.cursor.execute(query, (value,))
        rows = self.cursor.fetchall()
        return rows

    def save_changes(self) -> None:
        self.conn.commit()

    def insert_chat(self, userid: int, role: str, content: str) -> None:
        if self.conn is None:
            self.connect()
        try:
            query = "INSERT INTO ChatHistory (userid, role, content) VALUES (?, ?, ?)"
            self.cursor.execute(query, (userid, role, content))
            self.conn.commit()
            print("Chat inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def execute_query(
        self, query: str, params: Tuple = ()
    ) -> List[Dict[str, Union[str, int, float]]]:

        if self.conn is None:
            self.connect()
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    dict(zip([column[0] for column in self.cursor.description], row))
                )

            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return []


database_dep = Annotated[Database, Depends(Database)]


class ChatService:
    def __init__(self, db_service: database_dep) -> None:
        self._db_service: Database = db_service
        self._table_name: str = "ChatHistory"

    def get_user_chat(self, user_id: str) -> List[MessageModel]:
        rows = self._db_service.get_all_by(
            self._table_name,
            "userid",
            user_id,
            select_properties=["userid", "role", "content"],
        )
        return [MessageModel(role=row[1], content=row[2]) for row in rows]

    def push_chat(self, user_id: str, chat: MessageModel) -> bool:
        new_chat_record = ChatRecord(
            id=None,
            userid=user_id,
            role=chat.role,
            content=chat.content,
            datetime=datetime.datetime.now(datetime.UTC),
        )
        self._db_service.insert(self._table_name, new_chat_record.model_dump())
        self._db_service.save_changes()
