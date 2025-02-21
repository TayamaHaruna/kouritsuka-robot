from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数からLINE Botの設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleスプレッドシートの設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
cred_path = "path/to/your/service_account.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)
sheet = client.open("LINE_BOT_GOAL_TRACKER").sheet1

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.lower()
    user_id = event.source.user_id

    if "今日のアポ数" in user_message:
        try:
            appt_count = int(user_message.split()[-1])
            sheet.append_row([user_id, "アポ", appt_count])
            reply = f"{appt_count}件のアポを記録しました!"
        except ValueError:
            reply = "入力形式が正しくありません。例: 今日のアポ数 5"

    elif "成果" in user_message:
    reply = "今週の成果を振り返りましょう！"

elif "記録一覧" in user_message:
    records = sheet.get_all_values()
    record_text = "\n".join([",".join(row) for row in records[-5:]])

    if record_text:
        reply = f"最近の記録:\n{record_text}"
    else:
        reply = "行動を記録できます！"

# 例としての出力内容
reply += "\n\n例：今日のアポ数 5\n記録一覧 と入力すると、直近のデータを表示できます。"

line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(debug=True)

