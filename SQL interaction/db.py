import psycopg2

DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = '999fya999'
DB_PORT = 5432

class BD (object):
    def __init__(self):
        self.conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        self.cur = self.conn.cursor()

    def get_users(self):
        sql = """
        SELECT *
        FROM users
        """
        self.cur.execute(sql)
        sql_result = self.cur.fetchall()

        ret = []
        for record in sql_result:
            ret.append(list(record))
        return ret

    def add_users(self, data):
        sql = f"""
        INSERT INTO users (id, tg_id, date, weight)
        VALUES ({data[0]}, {data[1]}, \'{data[2]}\', {data[3]})
        """

        # sql = 'INSERT INTO users (id, tg_id, date, weight)\n' + f'VALUES ({data[0]}, {data[1]}, ' + '\'' + data[2] + '\'' + f', {data[3]})'

        self.cur.execute(sql)
        self.conn.commit()

   