from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    TemplateSendMessage,ButtonsTemplate,URIAction,ImageSendMessage
)
import os, MeCab, requests

app = Flask(__name__)

#環境変数取得
ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)


def kiis_button():
    message_template = TemplateSendMessage(
        alt_text="webサイト",
        template=ButtonsTemplate(
            text="九州情報大学のwebサイトです",
            title="九州情報大学",
            image_size='cover',
            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/img_top_bnr02.jpg",
            actions=[
                URIAction(
                    uri="https://www.kiis.ac.jp/",
                    label="push!"
                )
            ]
        )
    )
    return message_template

def bus_button():
    message_template = TemplateSendMessage(
        alt_text="スクールバスの時刻表",
        template=ButtonsTemplate(
            text="九州情報大学バスの時刻表です",
            title="バスの時刻表",
            image_size="cover",
            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/uploads/2018/03/img_information_bus_01_02.jpg",
            actions=[
                URIAction(
                    uri="https://www.kiis.ac.jp/information/bus/",
                    label="push!"
                )
            ]
        )
    )
    return message_template

def questionnaire_button():
    message_template = TemplateSendMessage(
        alt_text="授業改善アンケート",
        template=ButtonsTemplate(
            text="授業改善アンケートです",
            title="アンケート",
            image_size="cover",
            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
            actions=[
                URIAction(
                    uri="http://sun.kiis.ac.jp/",
                    label="push!"
                )
            ]
        )
    )
    return message_template

def service_button():
    message_template = TemplateSendMessage(
        alt_text="情報処理室",
        template=ButtonsTemplate(
            text="パスワード変更はこちらから",
            title="情報処理室",
            image_size="cover",
            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
            actions=[
                URIAction(
                    uri="http://service.kiis.ac.jp/",
                    label="push!"
                )
            ]
        )
    )
    return message_template

def enkaku_button():
    message_template = TemplateSendMessage(
        alt_text="遠隔授業",
        template=ButtonsTemplate(
            text="遠隔授業",
            title="遠隔授業",
            image_size="cover",
            thumbnail_image_url="https://www.kiis.ac.jp/wp-content/themes/kiis/img/no-img01.jpg",
            actions=[
                URIAction(
                    uri="http://kiis.ac.jp/gakunai/enkaku",
                    label="push!"
                )
            ]
        )
    )
    return message_template


@app.route("/")
def hello_world():
    return "hello world!"


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
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=(TextMessage))
def handle_image_message(event):
    text = event.message.text
    

    if text in ['サイト','web','さいと','site','kiis','Web','KIIS','webサイト']:
        messages = kiis_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    elif text in ['バス','ばす','bus','Bus']:
        messages = bus_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    elif text in ['アンケート','改善','評価']:
        messages = questionnaire_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    elif text in ['情報処理室','サービス','メニュー','service', 'password', 'パスワード']:
        messages = service_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    elif text in ['遠隔','遠隔授業','remote','授業']:
        messages = enkaku_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    elif text in ['その他']:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="どのような要件ですか？"))
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="もう一度おねがいします。"))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
