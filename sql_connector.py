import sqlite3
import datetime

def create_table_messages ():
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("""CREATE TABLE messages(
        id integer primary key autoincrement,
        user_id integer,
        message_id integer,
        message_text text,
        notifi_datetime datetime2);""")
        connection2.commit()

#cursor2.execute("INSERT INTO GMT('ID', 'GMT') VALUES (?, ?)", (m.chat.id, m.text,))

def insert_message (user_id, message_id, message_text, notifi_datetime):
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("""INSERT INTO messages(
        user_id, message_id, message_text, notifi_datetime, status)
        VALUES (?, ?, ?, ?, 0)""", (user_id, message_id, message_text, notifi_datetime))
        connection2.commit()

def get_message_by_id (id):

    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("""SELECT * FROM messages where id =?""", (str(id)))
        return cursor2.fetchone()


def get_active_msgs ():
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("""SELECT * FROM messages where status = 0""")
        return cursor2.fetchall()


def set_msg_sent (db_msg_id):
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    #print (db_msg_id)
    with connection2:
        cursor2.execute("""UPDATE messages SET status = 1 where id = ?""", (str(db_msg_id),))
        connection2.commit()


if __name__ == '__main__':
    #id = 1
    """
    string = get_active_msgs ()
    for notifi in string:
        notification_id = notifi[0]
        user_id = notifi[1]
        notification_datetime = notifi[3]
        notification_status = notifi[4]
        get_dt = datetime.datetime.strptime(notifi[4], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() > get_dt:
            #print ('yep')
            set_msg_sent (notification_id)
        #else:
        #    print ('nope')
        #print (get_dt)
    string = get_active_msgs ()
    print (string)
    """
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        #cursor2.execute(("SELECT 'ID' FROM GMT WHERE 'ID' = '{}'").format(m.chat.id))
        cursor2.execute("SELECT GMT FROM GMT WHERE ID=?", (12312,))
    try:
        print (cursor2.fetchone()[0])
        print ('asdasd')
    except TypeError:
        print ('0')
