import sqlite3

import psycopg2 as psycopg2
import configparser


def create_connection ():
    config = configparser.ConfigParser()
    config.sections()
    config.read('db.ini')
    host = config['DB_CONNECTION']['host']
    port = config['DB_CONNECTION']['port']
    database = config['DB_CONNECTION']['database']
    user = config['DB_CONNECTION']['user']
    password = config['DB_CONNECTION']['password']
    return psycopg2.connect(host=host, port=port, database=database, user=user, password=password)


def insert_message (user_id, message_id, message_text, notifi_datetime):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO messages(
        user_id, message_id, message_text, notifi_datetime, status)
        VALUES (?, ?, ?, ?, 0)""", (user_id, message_id, message_text, notifi_datetime))
    connection.commit()
    connection.close()

def get_message_by_id (id):

    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("""SELECT * FROM messages where id =?""", (str(id)))
        return cursor2.fetchone()


def get_active_msgs ():
    connection2 = create_connection()
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("""SELECT * FROM messages where status = 0""")
        return cursor2.fetchall()
    connection.close()


def set_msg_sent (db_msg_id):
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    #print (db_msg_id)
    with connection2:
        cursor2.execute("""UPDATE messages SET status = 1 where id = ?""", (str(db_msg_id),))
        connection2.commit()

def getConfig ():
    connection = create_connection()
    cursor = connection.cursor()
    query = """select value from public.settings where "name"  = 'token' or "name" = 'proxy';"""
    cursor.execute(query)
    records = cursor.fetchall()
    token = records[0][0]
    proxy = records[1][0]
    connection.close()
    return token, proxy


if __name__ == '__main__':
     token, proxy = getConfig ()
     print (token, proxy)