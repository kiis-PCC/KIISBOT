import config   # 先ほど作成したconfig.pyをインポート
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
    CarouselTemplate,CarouselColumn, MessageAction, PostbackAction
)
# from memory_profiler import profile
import os, MeCab,requests
import logging

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

    
    meishi_list=[] 

    # site = kiis_button()

    # 各変数のカウンター
    kiis_count = 0
    bus_count = 0
    questionnaire_count = 0
    service_count = 0
    enkaku_count = 0
    campusplan_count = 0
    

    while node:
        if  "名詞," in node.feature:
            meishi_list.append(node.surface)
        print(node.surface,'  ',node.feature)
        node = node.next
        mojiretsu = ','.join(meishi_list)

    for m in meishi_list:

        if m in ['サイト','web','さいと','site','kiis','Web','KIIS','webサイト']:
            # messages_kiis = kiis_button()
            # ans_list.append(messages_kiis)
            if kiis_count > 0:
                kiis_count = kiis_count + 1
            else:
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
                kiis_count = kiis_count + 1
            
            
        if m in ['バス','ばす','bus','Bus']:
            # messages_bus = bus_button()
            # ans_list.append(messages_bus)
            if bus_count > 0:
                bus_count = bus_count + 1
            else:
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
                bus_count = bus_count + 1

        if m in ['アンケート','改善','評価']:
            # messages_questionnaire = questionnaire_button()
            # ans_list.append(messages_questionnaire)
            if questionnaire_count > 0:
                questionnaire_count = questionnaire_count + 1
            else:
                result = CarouselColumn(
                        thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
                        text="授業改善アンケートです",
                        title="アンケート",
                        actions=[
                            URIAction(
                                uri="http://sun.kiis.ac.jp/",
                                label="push!"
                            )
                        ]
                    )
                columns.append(result)
                questionnaire_count = questionnaire_count + 1


        if m in ['情報処理室','サービス','メニュー','service', 'password', 'パスワード']:
            # messages_service = service_button()
            # ans_list.append(messages_service)
            if service_count > 0:
                service_count = service_count + 1
            else:
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
                service_count = service_count + 1

        if m in ['遠隔','遠隔授業','remote','授業']:
            # messages_enkaku = enkaku_button()
            # ans_list.append(messages_enkaku)
            if enkaku_count > 0:
                enkaku_count = enkaku_count + 1
            else:
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
                enkaku_count = enkaku_count + 1

        if m in ['履修','履修登録','履修確認','成績','campusplan','CampusPlan','Campusplan']:
            # messages_campusplan = campusplan_button()
            # ans_list.append(messages_campusplan)
            if campusplan_count > 0:
                campusplan_count = campusplan_count + 1
            else:
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
                campusplan_count = campusplan_count + 1

    
        if m in ['その他']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="どのような要件ですか？"))
            break

   
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