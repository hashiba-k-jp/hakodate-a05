from flask import Flask, render_template, request, jsonify
from src.findNearestEvacuation.test import test_app
from src.findNearestEvacuation.find_evacuation_point import find_evacuation_point
# from src.getInfoFromJMA.getInfo import getInfo, Entry
from src.getInfoFromJMA.initData import initData
import pprint as pp

# get data from JMA and run the program each same time.
from initApp import initApp

import base64,hashlib,hmac #署名検証用
import os,sys
import psycopg2
import uuid
import secrets
from linebot.models import TextSendMessage
from linebot import(
    LineBotApi
)
import linebot

from funcs import *

app = Flask(__name__)

#各種定数を定義
DEBUG = os.environ.get('IS_DEBUG') == 'True' #デバッグ用のフラグ
CHANNEL_SECRET  = os.environ.get('CHANNEL_SECRET')
ROOT_URL = os.environ.get('ROOT_URL')
CONSOLE_ROOT_URL = '{ROOT_URL}/control'.format(
    ROOT_URL=ROOT_URL
)

@app.route('/control/<uuid:id>')
def control_console(id):
    #DBへのコネクションを作成
    conn = db_connect()
    cursor = conn.cursor()

    #DB上にidが存在するかを確認
    sql = "SELECT EXISTS (SELECT * FROM public.verify WHERE id='{}');".format(id)
    cursor.execute(sql)
    result = cursor.fetchone()[0]
    conn.commit()

    #データベース上に存在しない場合正規のリクエストではないため500を返す
    if result == False:
        cursor.close()
        conn.close()
        return '',500,{}
    else:
        cursor.close()
        conn.close()
        return render_template("control.html",title="避難所経路探索|登録",id=id)

@app.route('/control/form', methods=['POST'])
def control_form():
    #送信データから値を抽出
    user_uuid = request.form.get('user_uuid')
    user_accept = request.form.get('user_resistration_accept_checkbox')

    try:
        #DBのコネクションを作成
        conn = db_connect()
        cursor = conn.cursor()

        #user_accept==onの時ユーザーを登録
        if user_accept == '1':
            #DBからuserのidを取得
            sql = "SELECT user_id FROM public.verify WHERE id='{}';".format(user_uuid)
            cursor.execute(sql)
            user_id = cursor.fetchone()[0]
            conn.commit()

            #DBから函館の地域コードを取得
            sql = "SELECT id FROM public.area WHERE area_name='函館市';"
            cursor.execute(sql)
            area_id = cursor.fetchone()[0]
            conn.commit()

            #resistrationにすでに登録されているかを確認
            sql = 'SELECT EXISTS (SELECT * FROM public.resistration WHERE user_id={user_id} AND area_id={area_id});'.format(user_id=user_id,area_id=area_id)
            cursor.execute(sql)
            resistration_result = cursor.fetchone()[0]
            conn.commit()
                
            if resistration_result == True:
                cursor.close()
                conn.close()
                
                return render_template(
                    'resistration_result.html',
                    title='避難所経路探索|登録結果',
                    result='すでに登録されています',
                    result_text='登録した心当たりがない場合は管理者にお問い合わせください'
                )
            else:
                #resistrationに登録
                sql = "INSERT INTO public.resistration(user_id,area_id) VALUES('{user_id}','{area_id}');".format(
                    user_id = user_id,
                    area_id = area_id
                )
                cursor.execute(sql)
                conn.commit()

                #verifyからユーザーを削除
                sql = "DELETE FROM public.verify WHERE id = '{}';".format(user_uuid)
                cursor.execute(sql)
                conn.commit()

                cursor.close()
                conn.close()

                return render_template(
                    'resistration_result.html',
                    title='避難所経路探索|登録結果',
                    result='登録完了',
                    resulttext='登録が完了しました。このページを閉じてください'
                )
        else:
            #DBからユーザの情報を削除
            
            #userのidを取得
            sql = "SELECT user_id FROM public.verify WHERE id='{}'".format(user_uuid)
            cursor.execute(sql)
            id = cursor.fetchone()[0]
            conn.commit()
            
            #public.userからユーザ情報を削除
            sql = 'DELETE FROM public.user WHERE id={}'.format(id)
            cursor.execute(sql)
            conn.commit()
              
            cursor.close()
            conn.close()

            return render_template(
                'resistration_result.html',
                title='避難所経路探索|登録結果',
                result='情報削除完了',
                result_text='データベースからご利用者様の情報を削除しました。またのご利用をお待ちしています。'
            )
    except psycopg2.IntegrityError:
        print('SQL RERATION ERROR!!')
        
        return render_template(
            'resistration_result.html',
            title='避難所経路探索|登録結果',
            result='内部エラー',
            result_text='システム内部でエラーが発生しました。もう一度登録を試みてください。'
        )
        
        
@app.route('/webhock', methods=['POST'])
def webhock():

    data = request.get_json() #user_id抽出用のリクエストデータ(json)
    print('data_type:{}'.format(type(data)))
    body = request.get_data(as_text=True) #検証用のリクエストデータ(string)

    signature = request.headers.get('x-line-signature')

    conn = db_connect()

    if validation(body=body, signature=signature.encode('utf-8')) == True: #イベントの真贋判定
        
        for line in data["events"]:
            user_id=''
            #ソースがユーザからのイベントである場合のみuser_idを抽出
            if line['source']['type'] == 'user':
                user_id = line["source"]['userId']
            else:
                #ソースがユーザーからのイベントではない時400を返して処理を終える
                return '',200,{}

            #DB操作用のカーソルを作成
            cursor = conn.cursor()

            #user_idが既にDB上に存在しているか確認する
            sql = "SELECT EXISTS (SELECT * FROM public.user WHERE user_id='{}');".format(user_id)
            if DEBUG == True:
                print('SQL EXECUTE:{}'.format(sql))
            cursor.execute(sql)
            conn.commit()

            result = cursor.fetchone()
            print('Result:{}'.format(result))

            #存在しない時DBに登録
            if result[0] == False:
                sql = "INSERT INTO public.user(user_id) VALUES('{}');".format(user_id)
                cursor.execute(sql)
                conn.commit()

            #イベントがmessageである時送信されたテキストの解析
            if line['type'] == 'message':
                if line['message']['text'] == '登録' or line['message']['text'] == '初期設定':
                    #URL用のUUIDの生成
                    user_uuid = uuid.uuid4()

                    #DBからuserのidを取得
                    sql = "SELECT id FROM public.user WHERE user_id='{}'".format(user_id)
                    cursor.execute(sql)
                    id = cursor.fetchone()[0]
                    conn.commit()
                    
                    #public.verifyにユーザーの情報が存在する場合は削除する
                    sql ="SELECT EXISTS (SELECT * FROM public.verify WHERE user_id={});".format(id)
                    cursor.execute(sql)
                    
                    if cursor.fetchone()[0] == True:
                        sql = "DELETE FROM public.verify WHERE user_id={}".format(id)

                        cursor.execute(sql)
                        conn.commit()
                    else:
                        conn.commit()
                         
                    #DBにUUIDとverify_hash,userのidを記録
                    sql = "INSERT INTO public.verify(id,user_id) VALUES ('{uuid}',{user_id});".format(
                        uuid=user_uuid,
                        user_id=id
                    )
                    if DEBUG == True:
                        print('SQL EXECUTE:{}'.format(sql))
                    cursor.execute(sql)
                    conn.commit()

                    #ユーザにURLと認証コードを送信

                    #URLを送信
                    url_msg = '管理用コンソール用URL\nhttps://{root_url}/{uuid}'.format(
                        root_url=CONSOLE_ROOT_URL,
                        uuid=user_uuid
                    )
                    send_msg_with_line(user_id=user_id, msgs=[url_msg])

                    #DBとの接続を解除
                    cursor.close()
                    conn.close()
            
            #messageではない時200を返して処理を終了
            else:
                return '',200,{}

            #全ての処理が正常終了した時200を返す
            return '',200,{}

    else:
        #正規のリクエストではないため200を返して終了
        return 'Bad Request',400,{}

@app.route('/location', methods=['GET'])
def get_location_get():
    return render_template('gps_design.html', title='Get Location App')

@app.route('/location', methods=['POST'])
def get_location_post():
    lat = request.form['lat']
    lng = request.form['lng']
    userID = request.form['userID']
    warningCode = request.form['warningCode']
    print(lat, lng, userID, warningCode)
    # currentAddress = None
    # hazardType = <warningCode>
    # GPS = {'N':<lat>, 'E':<lng>}
    # userID = <userID>
    # isTest = False
    test_app()
    notiData = find_evacuation_point(
        currentAddress=None,
        hazardType=warningCode,
        isTest=False,
        GPS={
            'N': lat,
            'E': lng
        },
        userID=userID
    )
    pp.pprint(notiData)
    if not(notiData['ErrorCode'] is None):
        return jsonify({'message': notiData['ErrorCode']}), 500
    else:
        '''
        send_msg_with_line(
            user_id=notiData['userID'],
            msgs=notiData['url'],
        )
        '''

        return "completed!"

#署名検証用の関数
def validation(body,signature):
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    val_signature = base64.b64encode(hash)

    #ローカルでバック用のバイパス
    if DEBUG == True:
        return True

    if val_signature == signature:
        return True
    else:
        return False

if __name__ == "__main__":
    initApp()
    initData()
    app.run(debug=True, host='localhost', port=5001)

