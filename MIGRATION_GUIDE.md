# 週報管理システム - 会社PC移行手順書

## 📋 事前準備（自宅PC）

### 1. 移行用フォルダ作成
```batch
cd C:\Users\Treadmill\source\repos\WeeklyReport
```

### 2. 必要ファイルのみをパッケージ化
以下のファイル・フォルダを含むZIPファイルを作成：
- `app.py`
- `weekly_report_processor.py`
- `weekly_reports.db`
- `processed_ids.json`
- `static/` フォルダ（全内容）
- `templates/` フォルダ（全内容）
- `requirements.txt`
- `CLAUDE.md`

### 3. 認証情報ファイル（重要）
- `credentials.json` - Gmail API認証
- `vertex-key.json` - Google Cloud認証
- `token.pkl` - Gmail認証トークン（あれば）

---

## 🖥️ 会社PC設定手順

### ステップ1: Python環境確認
```batch
python --version
pip --version
```
※ Python 3.8以上が必要

### ステップ2: プロジェクトフォルダ作成
```batch
mkdir C:\Users\[ユーザー名]\WeeklyReport
cd C:\Users\[ユーザー名]\WeeklyReport
```

### ステップ3: ファイル配置
1. 作成したZIPファイルを解凍
2. すべてのファイルを `C:\Users\[ユーザー名]\WeeklyReport` に配置
3. 認証ファイルも同じフォルダに配置

### ステップ4: Python依存関係インストール
```batch
cd C:\Users\[ユーザー名]\WeeklyReport
pip install -r requirements.txt
```

### ステップ5: 認証設定確認
以下のファイルが存在することを確認：
- `credentials.json`
- `vertex-key.json`

---

## 🚀 起動・動作確認

### 1. Webアプリケーション起動
```batch
cd C:\Users\[ユーザー名]\WeeklyReport
python app.py
```

### 2. ブラウザでアクセス
```
http://127.0.0.1:5000
```

### 3. 動作確認項目
- [ ] ページが正常に表示される
- [ ] ファビコン（書類+チェックマーク）が表示される
- [ ] 週報一覧が表示される
- [ ] フィルタリング機能が動作する
- [ ] 統計情報が表示される

### 4. Gmail週報処理テスト
```batch
python weekly_report_processor.py
```

初回実行時：
1. ブラウザが自動で開く
2. Googleアカウントでログイン
3. 認証を許可
4. `token.pkl` ファイルが自動生成される

---

## ⚠️ トラブルシューティング

### エラー1: モジュールが見つからない
```
ModuleNotFoundError: No module named 'flask'
```
**解決方法**:
```batch
pip install flask flask-cors google-cloud-aiplatform google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### エラー2: データベースが見つからない
```
no such table: weekly_reports
```
**解決方法**:
1. `weekly_reports.db` ファイルが正しい場所にあるか確認
2. ファイルが破損していないか確認

### エラー3: Gmail認証エラー
```
認証に失敗しました
```
**解決方法**:
1. `credentials.json` が正しい場所にあるか確認
2. `token.pkl` を削除して再認証

### エラー4: Vertex AI認証エラー
```
google.auth.exceptions.DefaultCredentialsError
```
**解決方法**:
1. `vertex-key.json` が正しい場所にあるか確認
2. ファイル内容が破損していないか確認

---

## 📁 最終的なフォルダ構成

```
C:\Users\[ユーザー名]\WeeklyReport\
├── app.py
├── weekly_report_processor.py
├── weekly_reports.db
├── processed_ids.json
├── requirements.txt
├── CLAUDE.md
├── credentials.json
├── vertex-key.json
├── token.pkl (自動生成)
├── static\
│   ├── css\
│   │   └── style.css
│   ├── js\
│   │   ├── app_fixed.js
│   │   └── edit_functions.js
│   └── images\
│       ├── favicon.svg
│       ├── favicon-32x32.png
│       ├── favicon-16x16.png
│       └── apple-touch-icon.png
└── templates\
    └── index.html
```

---

## ✅ 移行完了チェックリスト

- [ ] Python環境確認完了
- [ ] 全ファイル配置完了
- [ ] 依存関係インストール完了
- [ ] Webアプリ起動成功
- [ ] ブラウザアクセス成功
- [ ] ファビコン表示確認
- [ ] 週報データ表示確認
- [ ] Gmail認証テスト完了
- [ ] 週報処理テスト完了

---

## 📞 サポート情報

**問題が発生した場合**:
1. エラーメッセージを正確に記録
2. どの手順で発生したかを確認
3. ファイルの配置場所を再確認

**最終更新**: 2024年8月31日