from datetime import datetime
import psycopg2 as psycopg2
import configparser



class DbHelper(object):

    config = configparser.ConfigParser()
    config.sections()
    config.read('db.ini')

    def __init__(self, config):
        self.host = config['DB_CONNECTION']['host']
        self.port = config['DB_CONNECTION']['port']
        self.database = config['DB_CONNECTION']['database']
        self.user = config['DB_CONNECTION']['user']
        self.password = config['DB_CONNECTION']['password']

    def create_connection(self):
        return psycopg2.connect(host=self.host,
                         port=self.port,
                         database=self.database,
                         user=self.user,
                         password=self.password)

    def insertMessage (self, user_id, message_id, message_text, notifi_datetime):
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("""INSERT INTO messages(
            user_id, message_id, message_text, notifi_datetime, status)
            VALUES (?, ?, ?, ?, 0)""", (user_id, message_id, message_text, notifi_datetime))
            connection.commit()

    def getMessageById (self, uid):
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("""SELECT * FROM messages where id =?""", (str(uid)))
            return cursor.fetchone()


    def getActiveMessages (self):
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("""SELECT * FROM messages where status = 0""")
            return cursor.fetchall()


    def setMessageSent (self, db_msg_id):
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("""UPDATE messages SET status = 1 where id = ?""", (str(db_msg_id),))
            connection.commit()

    def getConfig (self):
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("""select value from public.settings where "name"  = 'token' or "name" = 'proxy';""")
            records = cursor.fetchall()
            token = records[0][0]
            proxy = records[1][0]
            return token, proxy

    def getGMT(self, id):
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("SELECT GMT FROM GMT WHERE ID=?", (id,))
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return '0'

    def get_show_time(self, uid, tg_server_time):
        tg_server_time = datetime.datetime.utcfromtimestamp(int(tg_server_time))
        connection = self.create_connection()
        cursor = connection.cursor()
        with connection:
            cursor.execute("SELECT GMT FROM GMT WHERE ID=?", (uid,))
        try:
            gmt_val = cursor.fetchone()[0]
        except TypeError:
            gmt_val = '0'

        if gmt_val.count('+') == 1:
            hours = int(gmt_val.replace('+', ''))
            return tg_server_time + datetime.timedelta(hours=hours)

        elif gmt_val.count('-') == 1:
            hours = int(gmt_val.replace('-', ''))
            return tg_server_time - datetime.timedelta(hours=hours)

        else:
            return tg_server_time


