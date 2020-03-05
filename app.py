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
import os

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
    if text in ['サイト','web','さいと','site','kiis']:
        messages = kiis_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    elif text in ['バス','ばす','buss']:
        messages = bus_button()
        line_bot_api.reply_message(
        event.reply_token,
        messages)
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="もう一度おねがいします。"))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
