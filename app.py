# import config   # 先ほど作成したconfig.pyをインポート
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
    CarouselTemplate,CarouselColumn, MessageAction, PostbackAction, QuickReply, QuickReplyButton
)
# from memory_profiler import profile
import os, MeCab,requests
import logging
import datetime
import pytz

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

columns = []

def carousel():
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=columns
        )
    )
    return carousel_template_message

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
    kiis_bh = [10,10,10,10,12,12,12,13,13,14,14,14,15,15,16,16,17,17,17,18]
    kiis_bm = [9,19,32,56,12,25,42,12,42,12,26,42,12,46,8,42,20,45,59,13]

    # 太宰府駅発のバスのリスト 
    dz_bh = [8,8,8,8,9,9,9,9,10,10,10,10,11,12,12,12,13,13,14,14,14,15,15,16,16,17,17]
    dz_bm = [13,25,37,50,2,17,29,46,0,16,26,39,3,19,32,49,19,49,19,34,49,19,53,15,49,27,52]
    
    
    meishi_list=[] 

    # site = kiis_button()

    # 各変数のカウンター
    kiis_count = 0
    bus_count = 0
    questionnaire_count = 0
    service_count = 0
    enkaku_count = 0
    campusplan_count = 0
    qa_count = 0
    setup_count = 0
    attendance_count = 0
    wifi_count = 0

    # 順番を並び替えするためのリスト 
    change_list = []

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

            if m in ['遠隔','遠隔授業','remote','授業']:
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

            if m in ['qa', 'q&a', 'Q&A', 'まとめ', '質問']:
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
                
            if m in ["wifi","Wifi","Wi","wi","network","Network","ネットワーク","接続","設定","ワイファイ"]:
                if wifi_count > 0:
                    wifi_count = wifi_count + 1
                    change_list.remove("wifi_count")
                    change_list.insert(0, "wifi_count")

                else:
                    wifi_count = wifi_count + 1
                    change_list.append("wifi_count")

    if change_list==[]:
        for c in change_list:
            if c == "kiis_count":
                result = CarouselColumn(
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/img_top_bnr02.jpg",
                            text="九州情報大学のwebサイトです",
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
                            text="九州情報大学バスの時刻表です",
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
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
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
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
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
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
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
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
                            text="九州情報大学のQ＆Aサイトです",
                            title="九州情報大学Q＆A",
                            actions=[
                                URIAction(
                                    uri="https://arcane-savannah-59524.herokuapp.com/index",
                                    label="push!"
                                )
                            ]
                        )
                columns.append(result)

            if c == "setup_count":
                result = CarouselColumn(
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
                            text="setupアカウント作成手順",
                            title="setup",
                            actions=[
                                URIAction(
                                    uri="https://arcane-savannah-59524.herokuapp.com/setup",
                                    label="push!"
                                )
                            ]
                        )
                columns.append(result)

            if c == "attendance_count":
                result = CarouselColumn(
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
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

            if c == "wifi_count":
                result = CarouselColumn(
                            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
                            text="Wi-fi(KIISWLAN)の設定",
                            title="Wi-Fiの設定",
                            actions=[
                                URIAction(
                                    uri="https://arcane-savannah-59524.herokuapp.com/nw_info",
                                    label="push!"
                                )
                            ]
                        )
                columns.append(result)

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

    if not columns:
        moji = TextSendMessage(text="一致する言葉がありませんでした。")
        messages = TextSendMessage(text="もう一度おねがいします。")
    else:
        moji = TextSendMessage(text=mojiretsu + ' を検知しました。')
        messages = carousel()
        

    line_bot_api.reply_message(
    event.reply_token,
    [moji, messages])
    
    columns.clear()



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