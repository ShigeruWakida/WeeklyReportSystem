# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered weekly report management system that automatically processes Gmail emails using Google Cloud Vertex AI (Gemini) and provides a web interface for data management, filtering, and analytics.

## Key Dependencies

- Flask (`flask==3.1.2`) - Web framework
- Google APIs: `googleapiclient`, `google_auth_oauthlib` for Gmail access
- Google Cloud: `google.cloud.aiplatform`, `vertexai` for AI text analysis (Gemini 2.0 Flash)
- SQLite for local data storage
- Required credential files:
  - `credentials.json` - Gmail API OAuth credentials
  - `vertex-key.json` - Google Cloud service account key
  - `token.pkl` - OAuth token (auto-generated)

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run email processor
python weekly_report_processor.py

# Start web dashboard
python app.py

# Docker deployment
docker-compose up

# Production deployment with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## Architecture

Two main components:

1. **Email Processor** (`weekly_report_processor.py`):
   - Authenticates with Gmail API using OAuth2
   - Retrieves emails with "週報" label
   - Sends to Vertex AI (Gemini) for analysis
   - Extracts structured data (reporter, date, client info, products, content)
   - Stores in SQLite database
   - Tracks processed IDs in `processed_ids.json`

2. **Web Application** (`app.py`):
   - Flask dashboard at http://localhost:5000
   - RESTful API endpoints for report management
   - Real-time processing status via SSE
   - Filtering by reporter, client, product
   - Batch operations for deletion

## Configuration

Master data defined in `weekly_report_processor.py`:
- `REPORTER_LIST` - Valid report authors
- `EMPLOYEE_LIST` - Employee names for companion identification
- `PRODUCT_LIST` - Product catalog with standardization (e.g., "2020" → "TF-2020")
- `PROJECT_ID` - Google Cloud project ID (use env var `GOOGLE_CLOUD_PROJECT_ID`)
- `LOCATION` - Vertex AI region (default: "us-central1")

## Database Schema

```sql
CREATE TABLE weekly_reports (
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
);
```

## API Endpoints

- `GET /api/reports` - Retrieve filtered reports with pagination
- `PUT /api/reports/<id>` - Update report data
- `POST /api/delete_mail_reports` - Batch delete by mail ID
- `POST /api/run_processor` - Start email processing
- `GET /api/process_logs` - Get processing logs (SSE stream)

## Environment Variables

```bash
GOOGLE_CLOUD_PROJECT_ID="your-project-id"
SECRET_KEY="your-secret-key"
DATABASE_PATH="/path/to/weekly_reports.db"  # Optional, defaults to ./weekly_reports.db
```

## Security Notes

- Never commit `credentials.json`, `vertex-key.json`, or `token.pkl`
- Use environment variables for sensitive configuration
- OAuth2 authentication required for Gmail access
- Service account authentication for Vertex AI