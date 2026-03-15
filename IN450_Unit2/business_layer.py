import psycopg


class BusinessLayer:
    def __init__(self, server, database, user, password):
        self.server = server
        self.database = database
        self.user = user
        self.password = password

    def _connect(self):
        connection = psycopg.connect(
            host=self.server,
            dbname=self.database,
            user=self.user,
            password=self.password,
            port="5432"
        )
        return connection

    def test_login(self):
        connection = self._connect()
        connection.close()
        return True

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

    def get_count_in450c(self):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM in450c;")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0]