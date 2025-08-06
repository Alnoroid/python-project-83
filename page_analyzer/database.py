import psycopg2
from psycopg2.extras import DictCursor


class Database:
    def __init__(self, database_url):
        self.database_url = database_url

    def execute(self, query, params=None):
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                if cursor.description:
                    return cursor.fetchall()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()