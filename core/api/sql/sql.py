import mysql.connector


class SQL():
    def __init__(self, *, user='', password='', address='127.0.0.1', port=3306, database='', raise_on_warnings=True):
        config = {
            'user': user,
            'password': password,
            'host': address,
            'port': port,
            'database': database,
            'raise_on_warnings': raise_on_warnings
        }

        self.conn = None
        self.cursor = None

        try:
            self.conn = mysql.connector.connect(**config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def __del__(self):
        if self.conn is not None and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
        print("Connection closed.")

    def is_connected(self):
        return self.conn is not None and self.conn.is_connected()
