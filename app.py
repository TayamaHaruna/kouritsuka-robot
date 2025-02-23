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
        # ✅ デフォルトの返信を設定（どの条件にも当てはまらない場合のため）
    reply = "⚠ メッセージの内容が認識されませんでした"
    import re  # 正規表現を使う

def handle_message(event):
    user_message = event.message.text.lower()

    if "今日のアポ" in user_message:  # ← ここはOK
        try:  # ← try ブロックを正しくインデント
            # 半角・全角スペース統一
            normalized_message = re.sub(r"\s+", " ", user_message)
            normalized_message = zen_to_han(normalized_message)

            # 「今日のアポ数 5」「今日のアポ 5件」 などをサポート
            match = re.search(r"(\d+|[一二三四五六七八九十])件?", normalized_message)

            if match:  # if も try ブロック内に入れる
                appt_count = match.group(1).rstrip("件")
                appt_count = kanji_to_number(appt_count) if appt_count in "一二三四五六七八九十" else int(appt_count)

                print("✅ スプレッドシートに記録します！")
                sheet.append_row([user_id, "アポ", appt_count])
                reply = f"{appt_count}件のアポを記録しました！"
        except ValueError:
            reply = "入力形式が正しくありません。例: 今日のアポ数 5"
            
    if "成果" in user_message:
        reply = "今週の成果を振り返りましょう！"

elif "記録一覧" in user_message:
    try:
        print("📌 スプレッドシートのデータ取得を開始します")  # デバッグ用ログ
        records = sheet.get_all_values()  # スプレッドシートからデータ取得
        print(f"📋 取得データ (最初の5件): {records[:5]}")  # 確認用ログ

    except Exception as e:
        print(f"❌ スプレッドシート取得エラー: {str(e)}")  # エラー詳細を出力
        records = []  # エラー時は空リストを代入

    if records:
        print("✅ データが取得できました")  # 確認ログ
        record_text = "\n".join([" | ".join(row) for row in records[-5:]])  # 直近5件のデータ
        reply = f"📋 最新の記録:\n{record_text}"
    else:
        print("⚠️ 取得データなし")  # 確認ログ
        reply = "📋 まだ記録がありません。行動を記録しましょう！"

def handle_message(event):
    reply_token = event.reply_token  # eventを関数の引数で受け取る
    line_bot_api.reply_message(reply_token, TextSendMessage(text=reply))



