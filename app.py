from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 1. 宣告全域變數，初始化計數器
openai_message_counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 2. 在函式內宣告要修改外層的全域變數
    global openai_message_counter
    
    text1 = event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            # 在這裡加入 system 角色，設定 AI 的個性
            {"role": "system", "content": "你現在扮演一位溫柔、優雅且充滿智慧的氣質姊姊。你的說話語氣溫婉、體貼、成熟，常常帶有安撫與鼓勵的感覺，請用親切、知性的口吻來回答問題。"},
            {"role": "user", "content": text1}
        ],
        model="gpt-5-nano",
        temperature = 1, # 建議稍微調降一點(原本是1)，可以讓語氣更穩定、符合成熟氣質的人設
    )
    
    try:
        ret = response['choices'][0]['message']['content'].strip()
        
        # 3. 如果成功取得 OpenAI 的回覆，計數器就 +1
        openai_message_counter += 1
        
        # 4. 將計數器的資訊串接在原本的回覆內容後面
        ret = f"{ret}\n\n[系統提示] 這是 OpenAI 傳送的第 {openai_message_counter} 則訊息。"
        
    except:
        ret = '發生錯誤！'
        
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
