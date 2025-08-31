# 週報管理システム 運用ガイド

## 📋 運用フロー概要

1. **ローカルPC**: Gmail週報を処理してデータベース更新
2. **データベース**: 更新されたDBファイルをAWSへアップロード  
3. **AWS**: Webインターフェースでデータ閲覧・管理

---

## 🔄 日常運用手順

### ステップ1: ローカルで週報処理

#### 1-1. コマンドプロンプトを開く
```bash
cd C:\Users\Treadmill\source\repos\WeeklyReport
```

#### 1-2. 週報処理を実行
```bash
python weekly_report_processor.py
```

#### 1-3. 処理の流れ
1. Gmailから「週報」ラベルのメールを取得
2. 各メールごとに処理確認プロンプトが表示
   ```
   処理しますか？ (y/n):
   ```
   - `y`: 処理実行
   - `n`: スキップ
3. Vertex AIで内容解析
4. `weekly_reports.db`に保存
5. 処理済みIDを`processed_ids.json`に記録

---

## 📤 データベースアップロード手順

### 方法A: Elastic Beanstalkへ直接デプロイ（推奨）

#### A-1. デプロイ用フォルダの準備
```bash
# 1. with_db_deployフォルダに最新DBをコピー
copy weekly_reports.db with_db_deploy\

# 2. フォルダを開く
explorer with_db_deploy
```

#### A-2. ZIPファイル作成
1. `with_db_deploy`フォルダ内の全ファイルを選択（Ctrl+A）
2. 右クリック → 「送る」 → 「圧縮フォルダー」
3. ファイル名を設定（例: `WeeklyReport-20240831.zip`）

#### A-3. AWSへデプロイ
1. [AWS Elastic Beanstalk](https://console.aws.amazon.com/elasticbeanstalk)にアクセス
2. `WeeklyReportSystem-env`を選択
3. 「アップロードとデプロイ」をクリック
4. 作成したZIPファイルを選択
5. バージョンラベル: `db-update-20240831`（日付を含める）
6. 「デプロイ」をクリック

#### A-4. デプロイ完了確認
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

1. **バッチファイル作成**
   ```batch
   @echo off
   echo 週報処理を開始します...
   python weekly_report_processor.py
   echo 処理完了！
   pause
   ```

2. **定期実行設定**
   - Windowsタスクスケジューラーで自動実行
   - 毎週月曜日の朝に自動処理

3. **バックアップ自動化**
   ```batch
   copy weekly_reports.db backup\weekly_reports_%date:~0,4%%date:~5,2%%date:~8,2%.db
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

最終更新: 2024年8月31日