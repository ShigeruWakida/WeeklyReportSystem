# 週報管理システム 運用ガイド

## 📋 運用フロー概要

1. **ローカルPC**: Gmail週報を処理してデータベース更新
2. **データベース**: 更新されたDBファイルをAWSへアップロード  
3. **AWS**: Webインターフェースでデータ閲覧・管理

---

## 🔄 日常運用手順（自動化版）

### ステップ1: 自動デプロイスクリプト実行

#### 1-1. コマンドプロンプトを開く
```bash
cd C:\Data\VB\WeeklyReport
```

#### 1-2. 自動デプロイスクリプトを実行
```bash
python auto_deploy.py
```

#### 1-3. 処理の流れ（全自動）
スクリプトが以下を自動で実行します：

**ステップ1: 週報メール処理**
1. Gmailから「週報」ラベルのメールを取得
2. Vertex AI（Gemini 2.0 Flash）で内容解析
3. `weekly_reports.db`に保存
4. 処理済みIDを`processed_ids.json`に記録

**ステップ2: データベースコピー**
1. `weekly_reports.db`を`with_db_deploy/`にコピー
2. 既存ファイルがある場合は自動バックアップ（タイムスタンプ付き）
3. ファイルサイズを表示

**ステップ3: デプロイ用ZIPファイル作成**
1. `with_db_deploy/`の内容をZIPに圧縮
2. タイムスタンプ付きファイル名で保存（例: `weekly_reports_deploy_20251020_084621.zip`）
3. ファイルサイズと完了メッセージを表示

#### 1-4. 実行結果の確認
```
[OK] 週報処理が正常に完了しました
[OK] データベースファイルのコピーが完了しました
[OK] デプロイパッケージ作成完了: weekly_reports_deploy_20251020_084621.zip
   ファイルサイズ: 1.90 MB
```

---

## 📤 AWSへのデプロイ手順

### ZIPファイルのアップロード

#### 手順1: AWS管理画面にアクセス
1. [AWS Elastic Beanstalk](https://console.aws.amazon.com/elasticbeanstalk)にアクセス
2. `WeeklyReportSystem-env`を選択

#### 手順2: デプロイ実行
1. 「アップロードとデプロイ」をクリック
2. `auto_deploy.py`で作成されたZIPファイルを選択
   - ファイル名例: `weekly_reports_deploy_20251020_084621.zip`
3. バージョンラベル: タイムスタンプを含める（例: `db-update-20251020`）
4. 「デプロイ」をクリック

#### 手順3: デプロイ完了確認
- 約2-3分でデプロイ完了
- ヘルスステータスが「OK」（緑）になることを確認

---

### 方法B: S3経由でアップロード（将来の自動化向け）

#### B-1. AWS CLIセットアップ（初回のみ）
```bash
pip install awscli
aws configure
```

#### B-2. S3バケット作成（初回のみ）
```bash
aws s3 mb s3://weekly-reports-db-backup
```

#### B-3. DBファイルアップロード
```bash
# 現在の日付でバックアップ
set TODAY=%date:~0,4%%date:~5,2%%date:~8,2%
aws s3 cp weekly_reports.db s3://weekly-reports-db-backup/db-%TODAY%.db

# 最新版として上書き
aws s3 cp weekly_reports.db s3://weekly-reports-db-backup/latest.db
```

#### B-4. EC2インスタンスでダウンロード
```bash
# SSHでEC2にログイン後
aws s3 cp s3://weekly-reports-db-backup/latest.db /var/app/current/weekly_reports.db
```

---

## 📊 データ確認

### Webインターフェースアクセス
```
http://weeklyreportsystem-env.eba-cik4bt2c.ap-northeast-1.elasticbeanstalk.com
```

### 主な機能
- **週報一覧**: ページネーション対応
- **フィルタリング**: 報告者・客先・製品で絞り込み
- **統計表示**: 各種集計データ
- **データ編集**: IDクリックで個別編集
- **一括削除**: メール単位で削除

---

## 🔧 トラブルシューティング

### 問題1: Gmail認証エラー
```
エラー: 認証に失敗しました
```
**解決方法**:
1. `token.pkl`を削除
2. 再度`python weekly_report_processor.py`実行
3. ブラウザで認証

### 問題2: Vertex AIエラー
```
エラー: API呼び出しに失敗
```
**解決方法**:
1. `vertex-key.json`が存在することを確認
2. Google Cloudプロジェクトの課金状態確認
3. API有効化を確認

### 問題3: デプロイ失敗
```
ERROR: Failed to deploy application
```
**解決方法**:
1. ZIPファイル構造を確認（フォルダを含めない）
2. ファイルサイズ確認（512MB以下）
3. 以前の動作バージョンに戻す

---

## 📅 定期メンテナンス

### 週次作業
- [ ] 週報処理実行
- [ ] DBファイルアップロード
- [ ] Webインターフェースで確認

### 月次作業
- [ ] `processed_ids.json`のバックアップ
- [ ] 古いDBバックアップの削除
- [ ] AWSコスト確認

### 年次作業
- [ ] Gmail API認証の更新
- [ ] Vertex AI認証キーのローテーション
- [ ] 古いデータのアーカイブ

---

## 🚨 緊急時対応

### データベース破損時
```bash
# バックアップから復元
copy weekly_reports_backup.db weekly_reports.db
```

### 処理済みIDリセット
```bash
# すべてのメールを再処理したい場合
del processed_ids.json
```

### 以前のバージョンに戻す
1. AWS Elastic Beanstalk管理画面
2. 「アプリケーションバージョン」
3. 動作していたバージョンを選択
4. 「デプロイ」

---

## 📝 運用チェックリスト

### 週報処理前
- [ ] `credentials.json`が存在
- [ ] `vertex-key.json`が存在
- [ ] インターネット接続確認

### 週報処理後
- [ ] 処理件数の確認
- [ ] エラーメッセージの確認
- [ ] DBファイルサイズ確認

### アップロード後
- [ ] Webインターフェースで新データ確認
- [ ] フィルタリング動作確認
- [ ] 統計数値の妥当性確認

---

## 💡 効率化のヒント

1. **バッチファイル作成** (推奨)

   `start_weekly_deploy.bat`を作成：
   ```batch
   @echo off
   cd C:\Data\VB\WeeklyReport
   echo 週報処理とデプロイパッケージ作成を開始します...
   python auto_deploy.py
   echo.
   echo 処理完了！生成されたZIPファイルをAWSにアップロードしてください。
   pause
   ```

   このバッチファイルをダブルクリックするだけで全処理が実行されます。

2. **定期実行設定**
   - Windowsタスクスケジューラーで`auto_deploy.py`を自動実行
   - 毎週月曜日の朝に自動処理
   - ZIPファイルは自動生成されるので、手動アップロードのみ実施

3. **手動処理が必要な場合**

   週報処理のみ実行したい場合：
   ```bash
   python weekly_report_processor.py
   ```

---

## 📞 サポート情報

### ログファイル確認
- ローカル処理ログ: コンソール出力
- AWS環境ログ: Elastic Beanstalk → ログ → ログをリクエスト

### よくある質問

**Q: どのくらいの頻度で更新すべき？**
A: 週1回、月曜日の朝がおすすめです。

**Q: 複数人で運用できる？**
A: ローカル処理は1人、Web閲覧は複数人可能です。

**Q: データベースの容量制限は？**
A: SQLiteは最大2GBまで対応可能です。

---

最終更新: 2025年10月20日