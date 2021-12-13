# funcs stands for FUNCtionS

import os, sys
import psycopg2
from linebot.models import TextSendMessage
from linebot import(
    LineBotApi
)
import linebot

#各種定数を環境変数から取得
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

#LINEユーザにメッセージを送信する関数
def send_msg_with_line(user_id,msgs):
    send_msg = TextSendMessage(text='')
    try:
        line_bot_api = LineBotApi(ACCESS_TOKEN)

        for msg in msgs:
            send_msg = TextSendMessage(text=msg)
            line_bot_api.push_message(user_id,send_msg)
    except linebot.exceptions.LineBotApiError as e:
        print(e.error.message)
        print(e.error.details)

#DB接続用の関数
def db_connect():

    print('Connecting:DataBase')
    conn = ''
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except psycopg2.Error:
        print('Database connection failed!!') #DBとの接続に失敗した場合は終了する
        sys.exit()

    return conn
