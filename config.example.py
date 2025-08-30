# 設定ファイル例
# 実際の使用時は config.py として保存し、値を設定してください

import os

# Google Cloud設定
GOOGLE_CLOUD_PROJECT_ID = "your-google-cloud-project-id"
GOOGLE_CLOUD_LOCATION = "asia-northeast1"

# Flask設定
SECRET_KEY = "your-secret-key-here"

# Gmail API設定
GMAIL_CREDENTIALS_FILE = "credentials.json"
GMAIL_TOKEN_FILE = "token.pkl"

# Vertex AI設定
VERTEX_KEY_FILE = "vertex-key.json"

# データベース設定
DATABASE_FILE = "weekly_reports.db"
PROCESSED_IDS_FILE = "processed_ids.json"