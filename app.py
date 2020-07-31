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
mecab.parse('')
 

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
    

    while node:
        if  "名詞," in node.feature:
            meishi_list.append(node.surface)
        print(node.surface,'  ',node.feature)
        node = node.next

    for m in meishi_list:

        if m in ['サイト','web','さいと','site','kiis','Web','KIIS','webサイト']:
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

            

        if m in ['バス','ばす','bus','Bus']:
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
    

        if m in ['アンケート','改善','評価']:
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
            


        if m in ['情報処理室','サービス','メニュー','service', 'password', 'パスワード']:
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


        if m in ['遠隔','遠隔授業','remote','授業']:
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


        if m in ['履修','履修登録','履修確認','成績','campusplan','CampusPlan','Campusplan']:
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


        if m in ['その他']:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="どのような要件ですか？"))
            break

    messages = carousel()

    line_bot_api.reply_message(
    event.reply_token,
    messages)
    
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