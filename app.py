from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
# 環境変数が取得できているか確認
json_data = os.environ.get("GOOGLE_CREDENTIALS_JSON")

if json_data:
    print("✅ 環境変数が正常に取得できています")
    print("環境変数の中身（100文字まで表示）:", json_data[:100])  # JSONの一部だけ表示
else:
    print("❌ 環境変数が取得できていません！")

from flask import Flask, request  

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    return "OK", 200


@app.route("/")
def home():
    return "🚀 アプリは動作中！"

# 環境変数からLINE Botの設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Googleスプレッドシートの設定
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# Google API のスコープ
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 環境変数から認証情報を取得（修正ポイント）
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)

# Googleスプレッドシートに接続
client = gspread.authorize(creds)
spreadsheet_id = "1NhIrPEWzxRBowoFVzqU8BpcJ3pORy94AMsoKac2FH_s"  # GoogleスプレッドシートのID
sheet = client.open_by_key(spreadsheet_id).sheet1

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.lower()
    user_id = event.source.user_id

    if "今日のアポ数" in user_message:
        try:
            appt_count = int(user_message.split()[-1])
            sheet.append_row([user_id, "アポ", appt_count])
            reply = f"{appt_count}件のアポを記録しました！"
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
    reply += "\n\n例: 今日のアポ数 5\n記録一覧 と入力すると、直近のデータを表示できます。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(debug=True)

