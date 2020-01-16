#-*- coding: utf-8 -*-


import telebot
from telebot import types
from telebot import apihelper
from multiprocessing import Process
import schedule
import time
import datetime
import sqlite3
from sql_connector import insert_message, get_message_by_id, get_active_msgs, set_msg_sent
import flask
import json

with open ('config.json') as json_file:
    config = json.load(json_file)


connection = sqlite3.connect("settings.db")
cursor = connection.cursor()

token = config.get('config').get('api')
states = {}
msgs = {}
cur_date = {}
mesg_ids = {}
bot = telebot.TeleBot(token)

def get_gmt(id):
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("SELECT GMT FROM GMT WHERE ID=?", (id,))
    try:
        return cursor2.fetchone()[0]
    except TypeError:
        return '0'


def get_show_time(uid, tg_server_time):
    tg_server_time = datetime.datetime.utcfromtimestamp(int(tg_server_time))
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("SELECT GMT FROM GMT WHERE ID=?", (uid,))
    try:
        gmt_val = cursor2.fetchone()[0]
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



def generate_user(id, username, last_name, first_name):
    name = None
    result_str = None
    if username != None:
        result_str = username
    if first_name != None:
        name = (' ({})'.format(first_name))
    if last_name != None:
        name = (' ({0} {1})'.format(first_name, last_name))

    if name != None and result_str != None:
        result_str += name
    else:
        result_str = name
    return result_str


def prep_notification (user_id, send_msg, timer):
    if timer == 't_9':
        timer_send = datetime.datetime.now().replace(hour=9,minute=0,second=0,microsecond=0)
        timer_send = timer_send + datetime.timedelta(days=1)
    elif timer == 't_12:00':
        timer_send = datetime.datetime.now().replace(hour=12,minute=0,second=0,microsecond=0)
        timer_send = timer_send + datetime.timedelta(days=1)
    elif timer == 't_18:00':
        timer_send = datetime.datetime.now().replace(hour=18,minute=0,second=0,microsecond=0)
        timer_send = timer_send + datetime.timedelta(days=1)
    elif timer == 'test':
        timer_send = datetime.datetime.now().replace(hour=23,minute=39,second=0,microsecond=0)

    else:
        timer_send = (datetime.datetime.now() + datetime.timedelta(minutes=timer))

    with open('logs.log', 'a', encoding='utf-8') as logfile:
        logfile.write('---------\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), call.message.chat.id, send_txt, selected_time))
    insert_message (call.message.chat.id, call.message.chat.id, send_txt, selected_time)


def send_notification (user_id, send_msg):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton (text= 'Очистить', callback_data='delete')
    keyboard.add (btn1)
    try:
        bot.send_message(user_id, send_msg, reply_markup=keyboard, parse_mode='HTML')
    except apihelper.ApiException:
        bot.send_message(user_id, text='message text is empty')


@bot.message_handler(commands=['setgmt'])
def setgmt(m):

    bot.send_message (m.from_user.id, 'Укажите часовой свой часовой пояс (например +3)')
    states[m.from_user.id] = 'set_gmt'

@bot.message_handler(commands=['showgmt'])
def showgmt(m):
    connection2 = sqlite3.connect("settings.db")
    cursor2 = connection2.cursor()
    with connection2:
        cursor2.execute("SELECT GMT FROM GMT WHERE ID=?", (m.chat.id,))

    try:
        gmt_val = cursor2.fetchone()[0]
    except TypeError:
        gmt_val = 'Часовой пояс не задан и расчитывается как GMT 0, выполните команду /setgmt для установки'

    bot.send_message (m.chat.id, '{}'.format (gmt_val))


@bot.message_handler(content_types= ['video', 'photo', 'document'])
def start_handler(m):
    bot.send_message (m.chat.id, text='only text messages')


@bot.message_handler(content_types= ['text'])
def start_handler(m):

    if states.get(m.from_user.id) == 'set_time':
        try:
            user_gmt = get_gmt(m.chat.id)
            selected_time = datetime.datetime.strptime(m.text, '%d.%m.%y %H:%M')
            send_msg = msgs.get(m.from_user.id)

            states[m.from_user.id] = ''
            m_id = mesg_ids.get(m.chat.id)

            if user_gmt.count('+') == 1:
                hours = int(user_gmt.replace('+', ''))

            elif user_gmt.count('-') == 1:
                hours = int(user_gmt.replace('-', ''))

            else:
                hours = 0

            selected_time = selected_time - datetime.timedelta(hours=hours) + datetime.timedelta(hours=3)

            with open('logs.log', 'a', encoding='utf-8') as logfile:
                logfile.write('---------\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), m.chat.id, send_msg, selected_time))

            insert_message (m.from_user.id, m_id, send_msg, selected_time)
            bot.edit_message_text(chat_id=m.chat.id, message_id=m_id, text=send_msg, parse_mode='HTML')
            bot.send_message (m.chat.id, 'Напоминание установлено на {}'.format(datetime.datetime.strptime(m.text, '%d.%m.%y %H:%M')))
        except ValueError:
            bot.send_message (m.chat.id, text='Неверный формат даты')
            states[m.from_user.id] = ''

    elif states.get(m.from_user.id) == 'set_gmt':
        input_data = m.text


        count_p = m.text.count('+')
        count_m = m.text.count('-')
        check = count_m + count_p
        if check == 1:
            if m.text.replace('+', '').replace('-', '').isdigit():
                connection2 = sqlite3.connect("settings.db")
                cursor2 = connection2.cursor()
                with connection2:
                    cursor2.execute("SELECT * FROM GMT WHERE ID=?", (m.chat.id,))
                    connection2.commit()
                rows = cursor2.fetchall()
                ids = [row[0] for row in rows]
                if m.chat.id not in ids:
                    with connection2:
                        cursor2.execute("INSERT INTO GMT('ID', 'GMT') VALUES (?, ?)", (m.chat.id, m.text,))
                        connection2.commit()
                    bot.send_message (m.chat.id, text='Добавлено')
                    states[m.from_user.id] = ''
                else:
                    with connection2:
                        cursor2.execute("UPDATE GMT SET 'GMT' = ? WHERE ID = ?", (m.text, m.chat.id, ))
                        connection2.commit()
                    bot.send_message (m.chat.id, text='Обновлено')
                    states[m.from_user.id] = ''

            else:
                bot.send_message (m.chat.id, text='Неверный формат GMT')
                states[m.from_user.id] = ''

        else:
            bot.send_message (m.chat.id, text='Неверный формат GMT')
            states[m.from_user.id] = ''
    else:
        if m.forward_from == None:
            bot.send_message(m.chat.id, 'Для активации напоминания нужно переслать сообщение')
        else:
            user_gmt = get_gmt(m.chat.id)
            if user_gmt == '0':

                warning_msg = """ВНИМАНИЕ!
Не установлен часовой пояс, наберите команду '/setgmt', что бы его установить.
Время напоминаний будет установлено по GMT +0"""
                bot.send_message (m.chat.id, text=warning_msg,  parse_mode="HTML")
            msgs[m.chat.id] = m.text
            show_time = get_show_time(m.chat.id, m.date)
            date = show_time.strftime('%d.%m.%Y')
            hour = show_time.strftime('%H')
            minute = show_time.strftime('%M')
            keyboard = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton (text= '+', callback_data='ch_d_p_{}_{}'.format(show_time, m.message_id))
            btn2 = types.InlineKeyboardButton (text= '+', callback_data='ch_h_p_{}_{}'.format(show_time, m.message_id))
            btn3 = types.InlineKeyboardButton (text= '+', callback_data='ch_m_p_{}_{}'.format(show_time, m.message_id))
            btn4 = types.InlineKeyboardButton (text= date, callback_data='set_{}_{}'.format(show_time, m.message_id))
            btn5 = types.InlineKeyboardButton (text= hour, callback_data='set_{}_{}'.format(show_time, m.message_id))
            btn6 = types.InlineKeyboardButton (text= minute, callback_data='set_{}_{}'.format(show_time, m.message_id))
            btn7 = types.InlineKeyboardButton (text= '-', callback_data='ch_d_m_{}_{}'.format(show_time, m.message_id))
            btn8 = types.InlineKeyboardButton (text= '-', callback_data='ch_h_m_{}_{}'.format(show_time, m.message_id))
            btn9 = types.InlineKeyboardButton (text= '-', callback_data='ch_m_m_{}_{}'.format(show_time, m.message_id))
            keyboard.add (btn1, btn2, btn3)
            keyboard.add (btn4, btn5, btn6)
            keyboard.add (btn7, btn8, btn9)
            btn10 = types.InlineKeyboardButton (text= 'Установить напоминание', callback_data='set_{}_{}'.format(show_time, m.message_id))
            keyboard.add (btn10)
            btn11 = types.InlineKeyboardButton (text= 'Ввести время вручную', callback_data='btn7_{}'.format(m.message_id))
            keyboard.add (btn11)
            forward_user = generate_user(m.forward_from.id, m.forward_from.username, m.forward_from.last_name, m.forward_from.first_name)
            msg = ("""Message from <b>{0}</b>:
{1}""".format(forward_user, m.text))
            msgs[m.chat.id] = msg
            bot.send_message (m.chat.id, text=msg, reply_markup=keyboard, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call:  (call.data == 'null'))
def change_state  (call):
    msg = ('Для изменения времени напоминания используйте кнопки "+" или "-"')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)


@bot.callback_query_handler(func=lambda call:  (call.data[:4] == 'btn7'))
def change_state  (call):

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=('Задать время'))
    states[call.message.chat.id] = 'set_time'
    msgs[call.message.chat.id] = call.message.text
    msg = ('Введите дату и время напоминания в формате дд.мм.гг чч:мм')

    mesg_ids[call.message.chat.id]=call.message.message_id
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)


@bot.callback_query_handler(func=lambda call:  (call.data[:3] == 'ch_'))
def change_date  (call):
    """ ch_m_m_{} """
    """ 2019-09-25 08:52:32 """
    input_data = call.data.split('_')
    subject = input_data[1]
    pm = input_data[2]
    msg_id = input_data[3]



    cur_time = datetime.datetime.strptime(input_data[3], '%Y-%m-%d %H:%M:%S')
    if subject == 'd':
        delta = datetime.timedelta(days=1)
    elif subject == 'h':
        delta = datetime.timedelta(hours=1)
    elif subject == 'm':
        delta = datetime.timedelta(minutes=1)

    if pm == 'p':
        changed_time = cur_time + delta
    elif pm == 'm':
        changed_time = cur_time - delta

    date = changed_time.strftime('%d.%m.%Y')
    hour = changed_time.strftime('%H')
    minute = changed_time.strftime('%M')
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton (text= '+', callback_data='ch_d_p_{}_{}'.format(changed_time, msg_id))
    btn2 = types.InlineKeyboardButton (text= '+', callback_data='ch_h_p_{}_{}'.format(changed_time, msg_id))
    btn3 = types.InlineKeyboardButton (text= '+', callback_data='ch_m_p_{}_{}'.format(changed_time, msg_id))
    btn4 = types.InlineKeyboardButton (text= date, callback_data='set_{}_{}'.format(changed_time, msg_id))
    btn5 = types.InlineKeyboardButton (text= hour, callback_data='set_{}_{}'.format(changed_time, msg_id))
    btn6 = types.InlineKeyboardButton (text= minute, callback_data='set_{}_{}'.format(changed_time, msg_id))
    btn7 = types.InlineKeyboardButton (text= '-', callback_data='ch_d_m_{}_{}'.format(changed_time, msg_id))
    btn8 = types.InlineKeyboardButton (text= '-', callback_data='ch_h_m_{}_{}'.format(changed_time, msg_id))
    btn9 = types.InlineKeyboardButton (text= '-', callback_data='ch_m_m_{}_{}'.format(changed_time, msg_id))
    keyboard.add (btn1, btn2, btn3)
    keyboard.add (btn4, btn5, btn6)
    keyboard.add (btn7, btn8, btn9)
    btn10 = types.InlineKeyboardButton (text= 'Установить напоминание', callback_data='set_{}_{}'.format(changed_time, msg_id))
    keyboard.add (btn10)
    btn11 = types.InlineKeyboardButton (text= 'Ввести время вручную', callback_data='btn7_{}'.format(msg_id))
    keyboard.add (btn11)
    msg_text = msgs.get(call.message.chat.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text, reply_markup=keyboard, parse_mode='HTML')




@bot.callback_query_handler(func=lambda call:  (call.data[:4] == 'set_'))
def change_state  (call):
    input_data = call.data.split('_')
    user_time = input_data[1]
    msg_id = input_data[2]

    send_txt = msgs.get(call.message.chat.id)
    selected_time = datetime.datetime.strptime(user_time, '%Y-%m-%d %H:%M:%S')
    server_time = datetime.datetime.now()
    user_gmt = get_gmt(call.message.chat.id)

    if user_gmt.count('+') == 1:
        hours = int(user_gmt.replace('+', ''))
        selected_time = selected_time - datetime.timedelta(hours=hours)
    elif user_gmt.count('-') == 1:
        hours = int(user_gmt.replace('-', ''))
        selected_time = selected_time + datetime.timedelta(hours=hours)

    selected_time = selected_time + datetime.timedelta(hours=3)

    with open('logs.log', 'a', encoding='utf-8') as logfile:
        logfile.write('---------\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), call.message.chat.id, send_txt, selected_time))

    insert_message (call.message.chat.id, msg_id, send_txt, selected_time)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


#delete
@bot.callback_query_handler(func=lambda call:  (call.data == 'delete'))
def change_state  (call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

def check_pending():
    while True:
        print ('check notifi')
        notifi_list = get_active_msgs ()
        print ('found ', len(notifi_list), ' notifis')
        for notifi in notifi_list:
            notification_id = notifi[0]
            user_id = notifi[1]
            notification_text = notifi[3]
            notification_datetime = notifi[4]
            get_dt = datetime.datetime.strptime(notifi[4], '%Y-%m-%d %H:%M:%S')
            print (datetime.datetime.now())
            print (get_dt)
            if datetime.datetime.now() > get_dt:
                send_notification (user_id, notification_text)
                set_msg_sent (notification_id)
        time.sleep (5)





if __name__ == '__main__':
    p1 = Process(target=check_pending, args=())
    p1.start()
    while True:
        try:
            print ('Listernig...')
            bot.polling(none_stop=True)
        except Exception as e:
            print (e)
            time.sleep(5)
