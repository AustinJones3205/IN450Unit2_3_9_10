import psycopg

class BusinessLayer:
    def __init__(self, user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.database = database

    def _connect(self):
        connection = psycopg.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port="5432",
            dbname=self.database
        )
        return connection

    def get_count_in450a(self):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM in450a;")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0]

    def get_names_in450b(self):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("SELECT first_name, last_name FROM in450b;")
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        names = []
        for row in rows:
            names.append(f"{row[0]} {row[1]}")

        return names

    def get_in450a_preview(self, limit=25):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT time, source, destination, protocol, length, info FROM in450a LIMIT %s;",
            (limit,)
        )
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows

    def get_in450b_preview(self, limit=25):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT first_name, last_name, email, source, destination FROM in450b LIMIT %s;",
            (limit,)
        )
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows
