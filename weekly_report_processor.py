import os
import pickle
import base64
import json
import sqlite3
import time
import warnings
import sys

# Windows での UTF-8 出力を強制
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Vertex AI SDK 非推奨警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module="vertexai.generative_models._generative_models")
warnings.filterwarnings("ignore", message="This feature is deprecated.*")
warnings.filterwarnings("ignore", message=".*deprecated as of June 24, 2025.*")

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel

# --------------------
# 設定
# --------------------
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "your-project-id")  # Google Cloud プロジェクトID
LOCATION = "asia-northeast1"     # Vertex AI ロケーション（東京）
DB_FILE = "weekly_reports.db"    # SQLite DBファイル
PROCESSED_FILE = "processed_ids.json"

# 報告者リスト（敬称なし）
REPORTER_LIST = ["西田","村田","田村","上島","藤原","柳澤","八木"]

# 同行社員リスト（敬称なし）
EMPLOYEE_LIST = ["藤原","柳澤","八木","岩下","西田","村田","田村","上島","社長",
                 "会長","和木田","土屋","小松原","大久保","有村","鈴木"]

# 製品名リスト
PRODUCT_LIST = ["DMA-03","PDL-06-SA","PDL-06","DPA-06","TF-3020","TF-3040","TFG-4060","TF-4060","TF-4060-G","TF-6090",
               "TF-90100","M3D-EL-FP-U","M3D-EL-W","M3D-EL-FP-A","TF-2020","HapLog","YAWASA","ゆびレコーダー","シートトレーサー",
               "IMS-SD","TRC","WTRC","VibraScope","ステアリングセンサ","野球ボールセンサ","FP内蔵ピッチャーマウンド","DSS300-HR","DLR1200","トレッドミル"]

# --------------------
# Gmail 認証
# --------------------
creds = None
if os.path.exists('token.pkl'):
    with open('token.pkl', 'rb') as token_file:
        creds = pickle.load(token_file)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.pkl', 'wb') as token_file:
        pickle.dump(creds, token_file)

service = build('gmail', 'v1', credentials=creds)

# --------------------
# Vertex AI 初期化
# --------------------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex-key.json"
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-1.5-flash")

# --------------------
# DB初期化
# --------------------
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mail_id TEXT,
    report_date TEXT,
    reporter TEXT,
    client_name TEXT,
    client_department TEXT,
    client_person TEXT,
    employee_name TEXT,
    product_name TEXT,
    content TEXT
)
''')
conn.commit()

# --------------------
# 処理済みID読み込み
# --------------------
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed_ids = set(json.load(f))
else:
    processed_ids = set()

# --------------------
# 週報ラベルID取得
# --------------------
labels = service.users().labels().list(userId='me').execute().get('labels', [])
label_id = next((l['id'] for l in labels if l['name'] == '週報'), None)
if not label_id:
    print("ラベル「週報」が見つかりません")
    exit()

# --------------------
# 週報メールID取得
# --------------------
all_messages = []
page_token = None
while True:
    results = service.users().messages().list(
        userId='me',
        labelIds=[label_id],
        pageToken=page_token
    ).execute()
    msgs = results.get('messages', [])
    all_messages.extend(msgs)
    page_token = results.get('nextPageToken')
    if not page_token:
        break

# 最新順
all_messages.sort(key=lambda x: int(x['id'], 16), reverse=True)

# 処理状況の表示
print(f"週報ラベルのメール: {len(all_messages)}件")
print(f"処理済み: {len(processed_ids)}件")
print(f"未処理: {len(all_messages) - len(processed_ids)}件")
print("\n週報処理を開始します...\n")

# --------------------
# AI解析関数
# --------------------
def process_weekly_report(subject, body, sender, date):
    prompt = f"""
このメールを解析して、純粋なJSON形式のみで出力してください。
マークダウンや```記号は使わないでください。
案件内容は、読みやすいように適切に改行を入れつつ整形してください。

重要な変換ルール：
- 客先名は必ず簡略化すること
  例：本田技研工業株式会社→ホンダ、トヨタ自動車株式会社→トヨタ、
      株式会社日立製作所→日立、ソニー株式会社→ソニー、
      三菱電機株式会社→三菱電機、富士通株式会社→富士通
- 株式会社、有限会社、合同会社などの会社形態は除去
- 一般的な通称がある場合は通称を使用
- 製品名は、以下のルールで省略すること
  - USL06-**-**: USL06
  - USL08-**-**: USL08
  - IMS-SD-H-*: IMS-SD

出力形式：
{{
  "週報判定": true/false,
  "報告者": "報告者名（報告者リストから選択、敬称不要）",
  "報告日": "YYYY-MM-DD形式",
  "報告内容": [
    {{
      "客先名": "客先名（必ず簡略化・通称を使用）",
      "客先部署名": "客先部署名",
      "客先担当者名": "客先担当者名（敬称不要）",
      "同行社員名": "同行社員名（社員名リストから）",
      "製品名": "製品名",
      "案件内容": "案件内容"
    }}
  ]
}}

報告者リスト（この中から報告者を特定）：
{','.join(REPORTER_LIST)}

社員名リスト（同行社員の特定用）：
{','.join(EMPLOYEE_LIST)}

製品名リスト（この中から該当する製品名を選択、なければ記載されたとおりに記録）：
{','.join(PRODUCT_LIST)}

製品名検出のルール：
- 数字のみ（例：2020、3040、4060等）が製品名として記載されている場合は、TF-やDSA-等のプレフィックスを付けて製品名リストと照合してください
- 例：「2020」→「TF-2020」、「3040」→「TF-3040」として製品名リストにあるか確認
- リストに一致するものがあればその正式名称を使用し、なければ記載されたとおりに記録してください

メール送信者: {sender}
メール送信日: {date}
メール件名: {subject}
メール本文: {body}
"""
    response = model.generate_content(prompt)
    content = response.text
    
    # マークダウンのコードブロック記号を除去
    if content.startswith('```'):
        content = content.split('\n', 1)[1]
    if content.endswith('```'):
        content = content.rsplit('```', 1)[0]
    content = content.strip()
    
    try:
        return json.loads(content)
    except Exception as e:
        print(f"JSON解析エラー: {e}")
        print(f"応答内容: {content[:200]}...")
        return None

# --------------------
# DB登録関数
# --------------------
def db_insert(mail_id, report_date, reporter, report):
    c.execute('''
    INSERT INTO weekly_reports
    (mail_id, report_date, reporter, client_name, client_department, client_person, employee_name, product_name, content)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        mail_id,
        report_date,
        reporter,
        report.get("客先名"),
        report.get("客先部署名"),
        report.get("客先担当者名"),
        report.get("同行社員名"),
        report.get("製品名"),
        report.get("案件内容")
    ))
    conn.commit()

# --------------------
# メール処理ループ
# --------------------
for msg in all_messages:
    msg_id = msg['id']
    if msg_id in processed_ids:
        continue

    msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = msg_data['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
    sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
    date = next((h['value'] for h in headers if h['name'] == 'Date'), "")

    # 本文取得
    body = ""
    payload = msg_data['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    # AI解析
    start_time = time.time()
    result = process_weekly_report(subject, body, sender, date)
    elapsed = time.time() - start_time

    if result is None:
        print(f"メールID {msg_id} の解析に失敗しました")
        processed_ids.add(msg_id)
        continue

    # 解析結果を表示
    print(f"\n[{len(processed_ids)+1}/{len(all_messages)}] メールID: {msg_id}")
    print(f"送信者: {sender}")
    print(f"件名: {subject}")
    print(f"解析時間: {elapsed:.2f}秒")
    print("-"*60)
    
    # 週報判定
    if result.get("週報判定"):
        reporter = result.get("報告者")
        report_date = result.get("報告日")
        
        print(f"[OK] 週報と判定されました")
        print(f"  報告者: {reporter}")
        print(f"  報告日: {report_date}")
        print(f"  報告件数: {len(result.get('報告内容', []))}件")
        print("-"*60)
        
        # 各報告内容を表示
        for i, report in enumerate(result.get("報告内容", []), 1):
            print(f"\n【報告 {i}】")
            print(f"  客先名: {report.get('客先名') or '-'}")
            print(f"  客先部署: {report.get('客先部署名') or '-'}")
            print(f"  客先担当者: {report.get('客先担当者名') or '-'}")
            print(f"  同行社員: {report.get('同行社員名') or '-'}")
            print(f"  製品名: {report.get('製品名') or '-'}")
            print(f"  案件内容: {report.get('案件内容') or '-'}")
            
            # DBに登録
            db_insert(msg_id, report_date, reporter, report)
        
        print("\n" + "="*60)
        print(f"[完了] [{len(processed_ids)+1}/{len(all_messages)}] メールID {msg_id} をDBに登録しました")
    else:
        print(f"[スキップ] 週報ではないと判定されました")
        print("="*60)

    # 処理済みIDに追加
    processed_ids.add(msg_id)
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_ids), f, ensure_ascii=False, indent=2)

print(f"\n処理完了: {len(processed_ids)}件のメールを処理しました。")
print(f"データベースに登録された週報数を確認中...")

# 最終的なDB統計を表示
c.execute('SELECT COUNT(*) FROM weekly_reports')
total_reports = c.fetchone()[0]
c.execute('SELECT COUNT(DISTINCT mail_id) FROM weekly_reports')
unique_mails = c.fetchone()[0]
print(f"登録済み週報: {total_reports}件 ({unique_mails}通のメールから)")

conn.close()