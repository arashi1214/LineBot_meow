import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))


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
    if event.message.text == '本周新片':
        r = requests.get('http://www.atmovies.com.tw/movie/new/')
        r.encoding = 'utf-8'

        soup = BeautifulSoup(r.text, 'lxml')
        content = []
        for i, data in enumerate(soup.select('div.filmTitle a')):
            if i > 20:
                break
            content.append(data.text + '\n' + 'http://www.atmovies.com.tw' + data['href'])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='\n\n'.join(content))
        )
        
if __name__ == "__main__":
    app.run()