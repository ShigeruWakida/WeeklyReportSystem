# セキュリティガイド

## GitHub公開前の必須チェック項目

### ✅ 完了済み
- [x] `.gitignore` 作成 - 認証情報ファイルを除外
- [x] プロジェクトIDをハードコードから環境変数に変更
- [x] 設定例ファイル作成 (`config.example.py`)

### ⚠️ GitHub公開前に必ず実行

1. **認証情報ファイルの削除確認**
   ```bash
   rm -f credentials.json
   rm -f vertex-key.json  
   rm -f token.pkl
   rm -f weekly_reports.db
   rm -f processed_ids.json
   ```

2. **環境変数設定**
   ```bash
   export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
   export SECRET_KEY="your-secret-key"
   ```

## 認証ファイルの取得方法

### 1. Gmail API認証 (credentials.json)
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Gmail API有効化
3. OAuth2.0クライアントID作成（デスクトップアプリ）
4. `credentials.json` ダウンロード

### 2. Vertex AI認証 (vertex-key.json)
1. Google Cloud Consoleでサービスアカウント作成
2. Vertex AI User権限付与
3. キーファイル（JSON）生成・ダウンロード
4. `vertex-key.json` として配置

## 本番環境での注意事項

- 認証ファイルは適切な権限（600）で保護
- 定期的なキーローテーション実施
- ログ出力にセンシティブ情報含めない
- HTTPS通信の強制化

## 脆弱性報告
セキュリティ問題を発見した場合は、公開せずに直接連絡してください。