from flask import Flask, request, abort
from argparse import ArgumentParser

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    TemplateSendMessage,ButtonsTemplate,URIAction,ImageSendMessage,
    CarouselTemplate,CarouselColumn, MessageAction, PostbackAction, QuickReply, QuickReplyButton, FlexSendMessage
)
# from memory_profiler import profile
import os, MeCab,requests
import logging
import datetime
import pytz
import json

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(module)-18s %(funcName)-10s %(lineno)4s: %(message)s'
)


app = Flask(__name__)

mecab = MeCab.Tagger ("-Owakati")
# mecab = MeCab.Tagger ("-Ochasen")
mecab.parse('')

# line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)    # config.pyで設定したチャネルアクセストークン
# handler = WebhookHandler(config.LINE_CHANNEL_SECRET)    # config.pyで設定したチャネルシークレット

#環境変数取得
ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

columns = []  #カルーセルの内容を入れるリスト

# カルーセル
def carousel():
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=columns
        )
    )
    return carousel_template_message

def other():
    flex_message_json_string = """
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "その他",
                        "weight": "bold",
                        "size": "xl"
                    },
                    {
                        "type": "text",
                        "text": "下記の中から選んでください"
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "質問",
                        "text": "質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "遠隔授業",
                        "text": "遠隔"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "uri",
                        "label": "KIIS FAQ",
                        "uri": "https://kiisfaq.pythonanywhere.com/index"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "uri",
                        "label": "西鉄太宰府線",
                        "uri": "http://jik.nishitetsu.jp/trainroute?f=traintimetable&list=0002,0500&_ga=2.209808725.1929044545.1605859087-517787699.1605859087"
                        }
                    }
                    ]
                }
            }
        """
    
    flex_message_json_dict = json.loads(flex_message_json_string)

    flex_message = FlexSendMessage(
                alt_text='alt_text',
                # contentsパラメタに, dict型の値を渡す
                contents=flex_message_json_dict
            )
    return flex_message

def question():
    flex_message_json_string = """
                            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "weight": "bold",
                        "size": "sm",
                        "text": "質問したい内容はこちらにありますか？"
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "text": "wifi",
                        "label": "Wi-Fi(KIISWLAN)"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": "Setup",
                        "text": "setup"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "text": "共有",
                        "label": "共有フォルダ(share)"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "該当なし",
                        "text": "該当なし"
                        }
                    }
                    ],
                    "flex": 0
                }
                }
            """
    
    flex_message_json_dict = json.loads(flex_message_json_string)

    flex_message = FlexSendMessage(
                alt_text='alt_text',
                # contentsパラメタに, dict型の値を渡す
                contents=flex_message_json_dict
            )
    return flex_message

# UptimeRobotでアクセスさせるためのページ
@app.route("/")
def hello_world():
    return "hello world!"

# メッセージが送信された時
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    
    text=event.message.text

    node = mecab.parseToNode(text)
    # words = mecab.parse(text)

    # 時刻取得
    date = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    hour = date.hour
    minute = date.minute
    # 大学発のバスのリスト 
    kiis_bh = [10,10,10,11,12,12,13,13,14,14,14,15,15,15,16,16,17,17,17,18,18,19]
    kiis_bm = [9 ,20,32,39,27,40,10,42,10,28,42,12,35,56,10,42,20,45,59,13,50,10]

    # 太宰府駅発のバスのリスト 
    dz_bh = [8 ,8 ,8 ,8 ,9 ,9 ,9 ,9 ,10,10,10,10,11,12,12,13,13,14,14,14,15,15,16,16,16,17]
    dz_bm = [13,25,37,50,2 ,17,29,46,1 ,16,27,39,46,34,46,17,49,17,35,49,19,42,3 ,17,49,27]
    
    
    meishi_list=[] 

    # site = kiis_button()

    # 各変数のカウンター
    kiis_count = 0   #九州情報大学HP
    bus_count = 0    #バス
    service_count = 0  #情報処理室
    enkaku_count = 0  #遠隔授業
    campusplan_count = 0  #履修登録
    attendance_count = 0  #出席くん
    #自作サイトURL
    qa_count = 0  #FAQサイト
    setup_count = 0 #setup
    wifi_count = 0 #wifi
    gsuite_count = 0  #gsuite
    nw_count = 0  #KIISNW
    share_count = 0 #shareフォルダ
    nw_password_count = 0 #nwパスワード
    nw_miss_count = 0 #nwパスワードトラブル
    office_id_count = 0 #office資格情報
    outlook_count = 0 #outlook
    webmail_count = 0 #webmail
    nwdrive_count = 0 #個人ドライブの割当

    switch_count = 0 #電源が入らない
    mac_count = 0 #macでwindows
    network_retry_count = 0 #ネットワークが繋がらない

    # flex_message
    other_count = 0 #その他
    question_count = 0 #質問

    # 順番を並び替えするためのリスト 
    change_list = []

        # 例外処理
    exception_list = []

    #レビュー
    review = []

    #学籍番号登録
    registration = []

    while node:
        if  "名詞," in node.feature:
            meishi_list.append(node.surface)
        print(node.surface,'  ',node.feature)
        node = node.next
        mojiretsu = ','.join(meishi_list)

    for m in meishi_list:
        if m in ['バス','ばす','bus','Bus']:
            items=[
                    QuickReplyButton(
                        action=MessageAction(label="時刻表", text="時刻")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="大学発の次のバス", text="return")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="太宰府駅発の次のバス", text="go")
                    )
                ]
            messages = TextSendMessage(text="バスの時刻表について次の選択肢から選んでください。補講日など通常と違う日程の際は時刻表を選択してください。",
                        quick_reply=QuickReply(items=items)) 

            
            line_bot_api.reply_message(
            event.reply_token,
            messages = messages)
        
        elif m in ['return']:
            for time in range(19):
                if int(hour) == kiis_bh[time] and int(minute) <= kiis_bm[time]: #次の時間
                    bus_h = str(hour)
                    bus_m = str(kiis_bm[time])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="次の大学発のバスは"+bus_h+"時"+bus_m+"分です。")
                    )
                    break
                elif int(hour) == kiis_bh[time] and int(minute) >= kiis_bm[time] and kiis_bh[time] < kiis_bh[time+1]: #次の時間のhourが変わる時
                    bus_h = str(kiis_bh[time+1])
                    bus_m = str(kiis_bm[time+1])    
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="次の大学発のバスは"+bus_h+"時"+bus_m+"分です。") #現在の時間帯にバスがない時
                    )
                    break
                elif int(hour) != kiis_bh[time] and int(hour) < kiis_bh[time] :
                    bus_h = str(kiis_bh[time])
                    bus_m = str(kiis_bm[time])    
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="次の大学発のバスは"+bus_h+"時"+bus_m+"分です。")
                    )
                    break

        elif m in ['go']:
            for time in range(26):
                if int(hour) == dz_bh[time] and int(minute) <= dz_bm[time]: #次の時間
                    bus_h = str(hour)
                    bus_m = str(dz_bm[time])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="次の太宰府駅発のバスは"+bus_h+"時"+bus_m+"分です。")
                    )
                    break
                elif int(hour) == dz_bh[time] and int(minute) >= dz_bm[time] and dz_bh[time] < dz_bh[time+1]: #次の時間のhourが変わる時
                    bus_h = str(dz_bh[time+1])
                    bus_m = str(dz_bm[time+1])    
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="次の太宰府駅発のバスは"+bus_h+"時"+bus_m+"分です。") #現在の時間帯にバスがない時
                    )
                    break
                elif int(hour) != dz_bh[time] and int(hour) < dz_bh[time] :
                    bus_h = str(dz_bh[time])
                    bus_m = str(dz_bm[time])    
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="次の太宰府駅発のバスは"+bus_h+"時"+bus_m+"分です。")
                    )
                    break
        elif m in ['授業','時間']:
            items=[
                    QuickReplyButton(
                        action=MessageAction(label="1", text="1")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="2", text="2")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="3", text="3")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="4", text="4")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="5", text="5")
                    ),
                ]
            messages = TextSendMessage(text="知りたい授業の時間を選択してください",
                        quick_reply=QuickReply(items=items)) 

            
            line_bot_api.reply_message(
            event.reply_token,
            messages = messages)

        elif m in ['1']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="1限の時間は8:50~10:20です。"))
            

        elif m in ['2']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="2限の時間は10:30~12:00です。"))
            

        elif m in ['3']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="3限の時間は12:50~14:20です。"))
            

        elif m in ['4']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="4限の時間は14:30~16:00です。"))
            

        elif m in ['5']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="5限の時間は16:10~17:40です。"))
            

        elif m in ['昼休み']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="昼休みの時間は12:00~12:50です。"))
            
        

        else:
            if m in ['サイト','web','さいと','site','kiis','Web','KIIS','webサイト']:
                if kiis_count > 0:
                    kiis_count = kiis_count + 1
                    change_list.remove("kiis_count")
                    change_list.insert(0, "kiis_count")

                else:
                    kiis_count = kiis_count + 1
                    change_list.append("kiis_count")

            # if m in ['バス','ばす','bus','Bus']:
            #     if bus_count > 0:
            #         bus_count = bus_count + 1
            #         change_list.remove("bus_count")
            #         change_list.insert(0, "bus_count")

            if m in ['時刻表','じこくひょう','schedule','時刻','スケジュール']:
                if bus_count > 0:
                    bus_count = bus_count + 1
                    change_list.remove("bus_count")
                    change_list.insert(0, "bus_count")

                else:
                    bus_count = bus_count + 1
                    change_list.append("bus_count")

            if m in ['情報処理室','サービス','メニュー','service', 'password', 'パスワード']:
                if service_count > 0:
                    service_count = service_count + 1
                    change_list.remove("service_count")
                    change_list.insert(0, "service_count")

                else:
                    service_count = service_count + 1
                    change_list.append("service_count")

            if m in ['遠隔','遠隔授業','remote','授業', '時間割', 'スケジュール', "講義"]:
                if enkaku_count > 0:
                    enkaku_count = enkaku_count + 1
                    change_list.remove("enkaku_count")
                    change_list.insert(0, "enkaku_count")

                else:
                    enkaku_count = enkaku_count + 1
                    change_list.append("enkaku_count")

            if m in ['履修','履修登録','履修確認','成績','campusplan','CampusPlan','Campusplan']:
                if campusplan_count > 0:
                    campusplan_count = campusplan_count + 1
                    change_list.remove("campusplan_count")
                    change_list.insert(0, "campusplan_count")

                else:
                    campusplan_count = campusplan_count + 1
                    change_list.append("campusplan_count")

            if m in ['setup', '設定', 'アカウント', 'account']:
                if setup_count > 0:
                    setup_count = setup_count + 1
                    change_list.remove("setup_count")
                    change_list.insert(0, "setup_count")

                else:
                    setup_count = setup_count + 1
                    change_list.append("setup_count")

            if m in ['qa', 'q&a', 'Q&A', 'まとめ']:
                if qa_count > 0:
                    qa_count = qa_count + 1
                    change_list.remove("qa_count")
                    change_list.insert(0, "qa_count")

                else:
                    qa_count = qa_count + 1
                    change_list.append("qa_count")
            
            if m in ['出席', 'attendance']:
                if attendance_count > 0:
                    attendance_count = attendance_count + 1
                    change_list.remove("attendance_count")
                    change_list.insert(0, "attendance_count")

                else:
                    attendance_count = attendance_count + 1
                    change_list.append("attendance_count")

            if m in ['gmail', 'gsuite', 'Gmail', 'Gsuite', 'mail', 'メール','web', 'Web', 'webmail', 'Webmail', 'WebMail', 'ウェブ', 'メール', '設定']:
                if gsuite_count > 0:
                    gsuite_count = gsuite_count + 1
                    change_list.remove("gsuite_count")
                    change_list.insert(0, "gsuite_count")

                else:
                    gsuite_count = gsuite_count + 1
                    change_list.append("gsuite_count")
                
            if m in ["wifi","Wifi","Wi","wi","network","Network","ネットワーク","接続","設定","ワイファイ"]:
                if wifi_count > 0:
                    wifi_count = wifi_count + 1
                    change_list.remove("wifi_count")
                    change_list.insert(0, "wifi_count")

                else:
                    wifi_count = wifi_count + 1
                    change_list.append("wifi_count")

            if m in ["network","Network","ネットワーク","接続","設定","ワイファイ"]:
                if nw_count > 0:
                    nw_count = nw_count + 1
                    change_list.remove("nw_count")
                    change_list.insert(0, "nw_count")

                else:
                    nw_count = nw_count + 1
                    change_list.append("nw_count")

            if m in ['share', 'シェア', 'フォルダ', 'folder', '共有', '設定']:
                if share_count > 0:
                    share_count = share_count + 1
                    change_list.remove("share_count")
                    change_list.insert(0, "share_count")

                else:
                    share_count = share_count + 1
                    change_list.append("share_count")

            if m in ['nw', 'ネットワーク', 'パスワード', 'password', 'network']:
                if nw_password_count > 0:
                    nw_password_count = nw_password_count + 1
                    change_list.remove("nw_password_count")
                    change_list.insert(0, "nw_password_count")

                else:
                    nw_password_count = nw_password_count + 1
                    change_list.append("nw_password_count")

            if m in ['nw', 'ネットワーク', 'パスワード', 'password', 'network', '後', '使用']:
                if nw_miss_count > 0:
                    nw_miss_count = nw_miss_count + 1
                    change_list.remove("nw_miss_count")
                    change_list.insert(0, "nw_miss_count")

                else:
                    nw_miss_count = nw_miss_count + 1
                    change_list.append("nw_miss_count")


            if m in ['office', 'Office', 'word', 'Word', 'excel', 'Excel', 'powerpoint', 'Powerpoint', '資格', '情報', 'ID', 'パスワード', '入力']:
                if office_id_count > 0:
                    office_id_count = office_id_count + 1
                    change_list.remove("office_id_count")
                    change_list.insert(0, "office_id_count")

                else:
                    office_id_count = office_id_count + 1
                    change_list.append("office_id_count")

            if m in ['outlook', 'Outlook', 'メール', 'mail', 'Mail']:
                            if outlook_count > 0:
                                outlook_count = outlook_count + 1
                                change_list.remove("outlook_count")
                                change_list.insert(0, "outlook_count")

                            else:
                                outlook_count = outlook_count + 1
                                change_list.append("outlook_count")

            if m in ['web', 'Web', 'webmail', 'Webmail', 'WebMail', 'mail', 'Mail', 'ウェブ', 'メール', '設定']:
                if webmail_count > 0:
                    webmail_count = webmail_count + 1
                    change_list.remove("webmail_count")
                    change_list.insert(0, "webmail_count")

                else:
                    webmail_count = webmail_count + 1
                    change_list.append("webmail_count")

            if m in ['ドライブ', 'わりあて', '割り当て', '個人', '設定']:
                if nwdrive_count > 0:
                    nwdrive_count = nwdrive_count + 1
                    change_list.remove("nwdrive_count")
                    change_list.insert(0, "nwdrive_count")

                else:
                    nwdrive_count = nwdrive_count + 1
                    change_list.append("nwdrive_count")

            if m in ['電源', 'スイッチ', 'ボタン', 'power', 'Power', 'windows', 'Windows']:
                if switch_count > 0:
                    switch_count = switch_count + 1
                    change_list.remove("switch_count")
                    change_list.insert(0, "switch_count")

                else:
                    switch_count = switch_count + 1
                    change_list.append("switch_count")

            if m in ['Mac', 'mac', 'macbook', 'Macbook', 'マック', 'bootcamp', 'OS', 'os']:
                if mac_count > 0:
                    mac_count = mac_count + 1
                    change_list.remove("mac_count")
                    change_list.insert(0, "mac_count")

                else:
                    mac_count = mac_count + 1
                    change_list.append("mac_count")

            if m in ['nw', 'NW', 'Network', 'network', 'KIISWLAN', 'kiiswlan', 'LAN', 'Wifi', 'wi', 'Wi', 'ネットワーク', '接続']:
                if network_retry_count > 0:
                    network_retry_count = network_retry_count + 1
                    change_list.remove("network_retry_count")
                    change_list.insert(0, "network_retry_count")

                else:
                    network_retry_count = network_retry_count + 1
                    change_list.append("network_retry_count")
            
            if m in ['インストール', 'install', 'Install', 'ウイルスバスター', 'ソフトウェア', 'ソフト', '一覧', '該当']:
                exception_list.append(m)
            
            if m in ['レビュー']:
                review.append(m)
            
            if m in ['その他']:
                other_count = other_count + 1
            
            if m in ['質問']:
                question_count = question_count + 1  

            #学籍番号の頭２桁
            #2030年になったらは23を追加
            if '21' in m:
                registration.append(m)
            
            if '22' in m:
                registration.append(m)
            # if m in ['インストール', 'install', 'Install', 'ウイルスバスター', 'ソフトウェア', 'ソフト']:
            #     moji = TextSendMessage(text=mojiretsu + ' を検知しました。')
                
            #     line_bot_api.reply_message(
            #     event.reply_token,
            #     [moji])
                
            #     columns.clear()
            #     change_list.clear()
                    # if m in ['その他']:
        #     line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text="どのような要件ですか？"))

#カルーセルの中身
    for c in change_list:
        if c == "kiis_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/img_top_bnr02.jpg",
                        text="九州情報大学のHPです",
                        title="九州情報大学",
                        actions=[
                            URIAction(
                                uri="https://www.kiis.ac.jp/",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "bus_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://www.kiis.ac.jp/wp-content/uploads/2018/03/img_information_bus_01_02.jpg",
                        text="スクールバスの時刻表です",
                        title="バスの時刻表",
                        actions=[
                            URIAction(
                                uri="https://www.kiis.ac.jp/information/bus/",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "service_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_school.png",
                        text="パスワード変更はこちらから",
                        title="情報処理室",
                        actions=[
                            URIAction(
                                uri="http://service.kiis.ac.jp/",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "enkaku_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_school.png",
                        text="遠隔授業の一覧です",
                        title="遠隔授業",
                        actions=[
                            URIAction(
                                uri="https://www.kiis.ac.jp/gakunai/enkaku",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "campusplan_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_school.png",
                        text="履修登録はこちらから",
                        title="CampusPlan",
                        actions=[
                            URIAction(
                                uri="https://kiis-web.campusplan.jp/gakusei/web/CplanMenuWeb/UI/LoginForm.aspx",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "qa_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="九州情報大学のQ＆Aサイトです",
                        title="九州情報大学FAQ",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/index",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "setup_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="setupアカウント作成手順",
                        title="setup",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/setup",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "attendance_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_school.png",
                        text="九州情報大学出席くん(kiis.online)です",
                        title="九州情報大学出席くん",
                        actions=[
                            URIAction(
                                uri="https://kiis.online",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "gsuite_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_school.png",
                        text="Gsuiteの設定はこちら",
                        title="Gsuite",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/gsuite",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "nw_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="学内でネットワークを使えるようになります",
                        title="KIISNW",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/kiisnw",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "share_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="共有フォルダ(share)の設定はこちら",
                        title="共有フォルダ(share)",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/share",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "nw_password_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="有効期限等について説明します",
                        title="ネットワークのパスワードについて",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/nw_password",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "nw_miss_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="パスワード変更後に使えなくなった場合はこちら",
                        title="ネットワークのパスワードのトラブル",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/nw_miss",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "office_id_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="Word,Excelなどでユーザー名とパスワードの入力が求められる時の対処法",
                        title="Officeでパスワードを聞かれるとき",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/office_id",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "outlook_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="2020年度以降に入学された方向けの内容です",
                        title="Outlookの設定",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/outlook",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "webmail_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="WebMailサービスの利用方法を説明します",
                        title="WebMailについて",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/webmail",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)

        if c == "nwdrive_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="一人当たり1GBの容量を持つ、ネットワークドライブが利用できます。",
                        title="個人用ドライブの割り当てについて",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/nwdrive",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)
        if c == "wifi_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="学内どこでも使えるWi-fiです",
                        title="Wi-Fi(KIISWLAN)の設定",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/nw_info",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)
        if c == "switch_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="PCが使えなくなったら試してみてください",
                        title="PCの電源が入らない時",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/power",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)
        if c == "mac_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="Bootcampの説明になります",
                        title="MacでWindowsを動かしたい時",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/bootcamp",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)
        if c == "network_retry_count":
            result = CarouselColumn(
                        thumbnail_image_url="https://kiisfaq.pythonanywhere.com/static/images/line_kiisfaq.png",
                        text="うまく接続できない時に試してみてください",
                        title="ネットワークに接続できない時",
                        actions=[
                            URIAction(
                                uri="https://kiisfaq.pythonanywhere.com/bootcamp",
                                label="push!"
                            )
                        ]
                    )
            columns.append(result)
        
        
            
    if review:
        moji = TextSendMessage(text="ありがとうございます。今後の研究の参考にさせていただきます。")
        #メッセージ送信
        line_bot_api.reply_message(
        event.reply_token,
        [moji])
        
        columns.clear()
        change_list.clear()
        review.clear()  

    elif registration:
        moji = TextSendMessage(text="登録ありがとうございます！")
        #メッセージ送信
        line_bot_api.reply_message(
        event.reply_token,
        [moji])
        
        columns.clear()
        change_list.clear()
        registration.clear()  

    elif exception_list:
        columns.clear()
        change_list.clear()
        exception_list.clear()

    elif other_count > 0:
        messages = other()
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
        other_count = 0

    elif question_count > 0:
        messages = question()
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
        question_count = 0
    else:
        if not columns:
            moji = TextSendMessage(text="一致する言葉がありませんでした。")
            messages = TextSendMessage(text="もう一度おねがいします。")
        else:
            moji = TextSendMessage(text=mojiretsu + ' を検知しました。')
            messages = carousel()
        
    #メッセージ送信
        line_bot_api.reply_message(
        event.reply_token,
        [moji, messages])
        
        columns.clear()
        change_list.clear()

        # if m in ['サイト','web','さいと','site','kiis','Web','KIIS','webサイト']:
        #     # messages_kiis = kiis_button()
        #     # ans_list.append(messages_kiis)
        #     if kiis_count > 0:
        #         kiis_count = kiis_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/img_top_bnr02.jpg",
        #                 text="九州情報大学のwebサイトです",
        #                 title="九州情報大学",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://www.kiis.ac.jp/",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         kiis_count = kiis_count + 1
            
            
        # if m in ['バス','ばす','bus','Bus']:
        #     # messages_bus = bus_button()
        #     # ans_list.append(messages_bus)
        #     if bus_count > 0:
        #         bus_count = bus_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/uploads/2018/03/img_information_bus_01_02.jpg",
        #                 text="九州情報大学バスの時刻表です",
        #                 title="バスの時刻表",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://www.kiis.ac.jp/information/bus/",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         bus_count = bus_count + 1

        # if m in ['アンケート','改善','評価']:
        #     # messages_questionnaire = questionnaire_button()
        #     # ans_list.append(messages_questionnaire)
        #     if questionnaire_count > 0:
        #         questionnaire_count = questionnaire_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="授業改善アンケートです",
        #                 title="アンケート",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://kiis.online/enquete/enquete.php",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         questionnaire_count = questionnaire_count + 1


        # if m in ['情報処理室','サービス','メニュー','service', 'password', 'パスワード']:
        #     # messages_service = service_button()
        #     # ans_list.append(messages_service)
        #     if service_count > 0:
        #         service_count = service_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="パスワード変更はこちらから",
        #                 title="情報処理室",
        #                 actions=[
        #                     URIAction(
        #                         uri="http://service.kiis.ac.jp/",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         service_count = service_count + 1

        # if m in ['遠隔','遠隔授業','remote','授業']:
        #     # messages_enkaku = enkaku_button()
        #     # ans_list.append(messages_enkaku)
        #     if enkaku_count > 0:
        #         enkaku_count = enkaku_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="遠隔授業の一覧です",
        #                 title="遠隔授業",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://www.kiis.ac.jp/gakunai/enkaku",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         enkaku_count = enkaku_count + 1

        # if m in ['履修','履修登録','履修確認','成績','campusplan','CampusPlan','Campusplan']:
        #     # messages_campusplan = campusplan_button()
        #     # ans_list.append(messages_campusplan)
        #     if campusplan_count > 0:
        #         campusplan_count = campusplan_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="履修登録はこちらから",
        #                 title="CampusPlan",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://kiis-web.campusplan.jp/gakusei/web/CplanMenuWeb/UI/LoginForm.aspx",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         campusplan_count = campusplan_count + 1

        # if m in ['qa', 'q&a', 'Q&A', 'まとめ', '質問']:
        #     # messages_enkaku = enkaku_button()
        #     # ans_list.append(messages_enkaku)
        #     if qa_count > 0:
        #         qa_count = qa_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="九州情報大学のQ＆Aサイトです",
        #                 title="九州情報大学Q＆A",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://arcane-savannah-59524.herokuapp.com/index",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         qa_count = qa_count + 1

        # if m in ['setup', '設定', 'アカウント', 'account']:
        #     # messages_enkaku = enkaku_button()
        #     # ans_list.append(messages_enkaku)
        #     if setup_count > 0:
        #         setup_count = setup_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="setupアカウント作成手順",
        #                 title="setup",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://arcane-savannah-59524.herokuapp.com/setup",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         setup_count = setup_count + 1

        # if m in ['出席', 'attendance']:
        #     # messages_enkaku = enkaku_button()
        #     # ans_list.append(messages_enkaku)
        #     if attendance_count > 0:
        #         attendance_count = attendance_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="九州情報大学出席くん(kiis.online)です",
        #                 title="九州情報大学出席くん",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://kiis.online",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         attendance_count = attendance_count + 1

        # if m in ["wifi","Wifi","Wi","wi","network","Network","ネットワーク","接続","設定","ワイファイ"]:
        #     # messages_enkaku = enkaku_button()
        #     # ans_list.append(messages_enkaku)
        #     if wifi_count > 0:
        #         wifi_count = wifi_count + 1
        #     else:
        #         result = CarouselColumn(
        #                 thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
        #                 text="Wi-fi(KIISWLAN)の設定",
        #                 title="Wi-Fiの設定",
        #                 actions=[
        #                     URIAction(
        #                         uri="https://arcane-savannah-59524.herokuapp.com/nw_info",
        #                         label="push!"
        #                     )
        #                 ]
        #             )
        #         columns.append(result)
        #         wifi_count = wifi_count + 1

        
    
        # if m in ['その他']:
        #     line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text="どのような要件ですか？"))
        #     break
#     text = event.message.text
#     if m in ['バス','ばす','bus','Bus']:
#         line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(
#             text="バスの時刻表について次の選択肢から選んでください",
#             quick_reply=QuickReply(
#                 items=[
#                 QuickReplyButton(
#                     action=MessageAction(label="時刻表", text="時刻")
#                 ),
#                 QuickReplyButton(
#                     action=MessageAction(label="大学発の次のバス", text="大学")
#                 ),
#                 QuickReplyButton(
#                     action=MessageAction(label="太宰府駅発の次のバス", text="太宰府")
#                 ),
#             ])))

#     if m in ['大学']:
#         for time in range(19):
#             if int(hour) == kiis_bh[time] and int(minute) <= kiis_bm[time]: #次の時間
#                 bus_h = str(hour)
#                 bus_m = str(kiis_bm[time])
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="次の大学発のバスは"+bus_h+"時"+bus_m+"分です。")
#                 )
#                 break
#             elif int(hour) == kiis_bh[time] and int(minute) >= kiis_bm[time] and kiis_bh[time] < kiis_bh[time+1]: #次の時間のhourが変わる時
#                 bus_h = str(kiis_bh[time+1])
#                 bus_m = str(kiis_bm[time+1])    
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="次の大学発のバスは"+bus_h+"時"+bus_m+"分です。") #現在の時間帯にバスがない時
#                 )
#                 break
#             elif int(hour) != kiis_bh[time] and int(hour) < kiis_bh[time] :
#                 bus_h = str(kiis_bh[time])
#                 bus_m = str(kiis_bm[time])    
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="次の大学発のバスは"+bus_h+"時"+bus_m+"分です。")
#                 )
#                 break
                

#     if m in ['太宰府']:
#         for time in range(19):
#             if int(hour) == dz_bh[time] and int(minute) <= dz_bm[time]: #次の時間
#                 bus_h = str(hour)
#                 bus_m = str(dz_bm[time])
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="次の太宰府駅発のバスは"+bus_h+"時"+bus_m+"分です。")
#                 )
#                 break
#             elif int(hour) == dz_bh[time] and int(minute) >= dz_bm[time] and dz_bh[time] < dz_bh[time+1]: #次の時間のhourが変わる時
#                 bus_h = str(dz_bh[time+1])
#                 bus_m = str(dz_bm[time+1])    
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="次の太宰府駅発のバスは"+bus_h+"時"+bus_m+"分です。") #現在の時間帯にバスがない時
#                 )
#                 break
#             elif int(hour) != dz_bh[time] and int(hour) < dz_bh[time] :
#                 bus_h = str(dz_bh[time])
#                 bus_m = str(dz_bm[time])    
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="次の太宰府駅発のバスは"+bus_h+"時"+bus_m+"分です。")
#                 )
#                 break

    # if not columns:
    #     moji = TextSendMessage(text="一致する言葉がありませんでした。")
    #     messages = TextSendMessage(text="もう一度おねがいします。")
    # else:
    #     moji = TextSendMessage(text=mojiretsu + ' を検知しました。')
    #     messages = carousel()
        

    # line_bot_api.reply_message(
    # event.reply_token,
    # [moji, messages])
    
    # columns.clear()



logging.debug("デバッグ")
logging.info("情報")

# if __name__ == "__main__":
#     app.run(host="localhost", port=8000)   # ポート番号を8000に指定



if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=int(os.environ.get('PORT', 8000)), help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    arg_parser.add_argument('--host', default='0.0.0.0', help='host')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, host=options.host, port=options.port)