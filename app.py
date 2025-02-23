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
    user_message = event.message.text.lower()  # 受信メッセージ
    print(f"📩 受信メッセージ: {user_message}")  # デバッグ用

    # ✅ コマンド（「記録一覧」など）をスプレッドシートに記録しない
    if user_message not in ["記録一覧", "最近の記録"]:  
        try:
            print("✅ スプレッドシートに記録します！")  # 確認ログ
            sheet.append_row([user_message])  # メッセージ内容のみ記録
            reply = f"📋 記録しました: {user_message}"
        except Exception as e:
            print(f"❌ 記録エラー: {str(e)}")  # エラー詳細を出力
            reply = "⚠ スプレッドシートへの記録に失敗しました"

    # ✅ 最新の記録を取得する処理
    elif user_message in ["記録一覧", "最近の記録"]:  
        try:
            print("📌 スプレッドシートのデータ取得を開始します")  # デバッグ用
            records = sheet.get_all_values()  # スプレッドシートからデータ取得
            print(f"📄 取得データ（最新5件）: {records[-5:]}")  # 確認用ログ

            if records:
                record_text = "\n".join([row[0] for row in records[-5:] if row])  # 最新5件取得
                reply = f"📄 最新の記録:\n{record_text}"
            else:
                reply = "📋 まだ記録がありません。行動を記録しましょう！"

        except Exception as e:
            print(f"❌ スプレッドシート取得エラー: {str(e)}")  # エラー詳細を出力
            reply = "⚠ 記録の取得に失敗しました"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
