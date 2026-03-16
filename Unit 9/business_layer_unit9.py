import logging
from typing import List

import psycopg


logger = logging.getLogger(__name__)


class BusinessLayer:
    def __init__(self, server: str, database: str, user: str, password: str):
        self.server = server
        self.database = database
        self.user = user
        self._connection = self._create_connection(password)
        password = None

    def _create_connection(self, password: str):
        connection = psycopg.connect(
            host=self.server,
            dbname=self.database,
            user=self.user,
            password=password,
            port="5432",
            connect_timeout=5,
        )
        return connection

    def test_login(self) -> bool:
        return self._connection is not None and not self._connection.closed

    def close(self) -> None:
        if self._connection is not None and not self._connection.closed:
            self._connection.close()

    def _ensure_connection(self) -> None:
        if self._connection is None or self._connection.closed:
            raise RuntimeError("Database session is closed.")

    def get_count_in450a(self) -> int:
        self._ensure_connection()
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM in450a;")
            result = cursor.fetchone()
        return result[0]

    def get_names_in450b(self) -> List[str]:
        self._ensure_connection()
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT first_name, last_name FROM in450b ORDER BY last_name, first_name;")
            rows = cursor.fetchall()
        return [f"{row[0]} {row[1]}" for row in rows]

    def get_count_in450c(self) -> int:
        self._ensure_connection()
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM in450c;")
            result = cursor.fetchone()
        return result[0]
