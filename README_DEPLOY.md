# 週報管理システム - デプロイメントガイド

## ローカル環境での実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# アプリケーション起動
python app.py
```

ブラウザで http://localhost:5000 にアクセス

## Docker での実行

```bash
# イメージビルド
docker build -t weekly-report-app .

# コンテナ起動
docker run -p 5000:5000 -v $(pwd)/weekly_reports.db:/app/data/weekly_reports.db weekly-report-app

# または docker-compose 使用
docker-compose up -d
```

## AWS へのデプロイ

### 方法1: AWS Elastic Beanstalk

1. EB CLI のインストール
```bash
pip install awsebcli
```

2. Elastic Beanstalk アプリケーションの初期化
```bash
eb init -p python-3.11 weekly-report-app --region ap-northeast-1
```

3. 環境の作成とデプロイ
```bash
eb create weekly-report-env
eb deploy
```

4. アプリケーションを開く
```bash
eb open
```

### 方法2: AWS ECS (Fargate)

1. ECR リポジトリ作成
```bash
aws ecr create-repository --repository-name weekly-report-app --region ap-northeast-1
```

2. Docker イメージをプッシュ
```bash
# ログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin [account-id].dkr.ecr.ap-northeast-1.amazonaws.com

# タグ付けとプッシュ
docker tag weekly-report-app:latest [account-id].dkr.ecr.ap-northeast-1.amazonaws.com/weekly-report-app:latest
docker push [account-id].dkr.ecr.ap-northeast-1.amazonaws.com/weekly-report-app:latest
```

3. ECS タスク定義とサービスを作成（AWS Console または CLI）

### 方法3: AWS Lambda + API Gateway (Serverless)

1. Serverless Framework のインストール
```bash
npm install -g serverless
npm install --save-dev serverless-python-requirements serverless-wsgi
```

2. デプロイ
```bash
serverless deploy --stage prod
```

## 環境変数

本番環境では以下の環境変数を設定してください：

- `SECRET_KEY`: Flask のシークレットキー（ランダムな文字列）
- `DATABASE_PATH`: SQLite データベースファイルのパス
- `AWS_REGION`: AWS リージョン（デフォルト: ap-northeast-1）

## データベースの永続化

### EBS (Elastic Beanstalk) の場合
- `.ebextensions/storage.config` を作成してEBSボリュームをアタッチ

### ECS/Fargate の場合
- EFS (Elastic File System) をマウント
- または RDS/Aurora に移行

### Lambda の場合
- S3 にデータベースファイルを保存
- または DynamoDB に移行

## セキュリティ考慮事項

1. **HTTPS の有効化**
   - AWS Certificate Manager で SSL 証明書を取得
   - ALB または CloudFront で HTTPS を設定

2. **認証の追加**
   - AWS Cognito または Auth0 との統合
   - Flask-Login による認証実装

3. **VPC の設定**
   - プライベートサブネットへの配置
   - セキュリティグループの適切な設定

4. **シークレット管理**
   - AWS Secrets Manager または Parameter Store の使用
   - 環境変数に直接記載しない

## モニタリング

- CloudWatch でログとメトリクスを監視
- X-Ray でトレーシング
- CloudWatch Alarms でアラート設定