# Installation Guide

Step-by-step setup instructions for WeeklyReportSystem

## Prerequisites

- Python 3.7 or higher
- Google Cloud Platform account
- Gmail account
- Git (for cloning repository)

## 1. Clone Repository

```bash
git clone https://github.com/ShigeruWakida/WeeklyReportSystem.git
cd WeeklyReportSystem
```

## 2. Python Environment Setup

### Option A: Using virtual environment (Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Option B: Using conda
```bash
conda create -n weekly-report python=3.8
conda activate weekly-report
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Google Cloud Setup

### 4.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your Project ID (you'll need this later)

### 4.2 Enable Required APIs

```bash
# Enable Gmail API
gcloud services enable gmail.googleapis.com

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

Or enable manually in the console:
- [Gmail API](https://console.developers.google.com/apis/library/gmail.googleapis.com)
- [Vertex AI API](https://console.developers.google.com/apis/library/aiplatform.googleapis.com)

## 5. Gmail API Authentication

### 5.1 Create OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Click "Create Credentials" → OAuth client ID
4. Choose "Desktop application"
5. Download the JSON file
6. Rename it to `credentials.json` and place in project root

### 5.2 Set up OAuth2 consent screen

1. Go to APIs & Services → OAuth consent screen
2. Choose "External" user type
3. Fill required information:
   - Application name: "WeeklyReportSystem"
   - User support email: your email
   - Developer contact: your email
4. Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
5. Add test users (your Gmail address)

## 6. Vertex AI Authentication

### 6.1 Create Service Account

1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: `weekly-report-ai`
4. Grant role: "Vertex AI User"
5. Click "Done"

### 6.2 Generate Key File

1. Click on created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose JSON format
5. Download and rename to `vertex-key.json`
6. Place in project root

## 7. Gmail Label Setup

1. Open Gmail
2. Create a new label named "週報" (Weekly Report)
   - Gmail → Settings → Labels → Create new label
3. Apply this label to your weekly report emails

## 8. Environment Configuration

Create environment variables:

### Windows (Command Prompt)
```cmd
set GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id
set SECRET_KEY=your-secure-secret-key
```

### Windows (PowerShell)
```powershell
$env:GOOGLE_CLOUD_PROJECT_ID="your-actual-project-id"
$env:SECRET_KEY="your-secure-secret-key"
```

### macOS/Linux (bash/zsh)
```bash
export GOOGLE_CLOUD_PROJECT_ID="your-actual-project-id"
export SECRET_KEY="your-secure-secret-key"
```

### Using .env file (Alternative)
Create `.env` file in project root:
```env
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id
SECRET_KEY=your-secure-secret-key
```

## 9. Initial Test

### 9.1 Test Gmail Connection
```bash
python -c "
import pickle, os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

with open('token.pkl', 'wb') as token:
    pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)
print('Gmail connection successful!')
"
```

### 9.2 Test Vertex AI Connection
```bash
python -c "
import os
import vertexai
from vertexai.generative_models import GenerativeModel

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex-key.json'

vertexai.init(project=project_id, location='asia-northeast1')
model = GenerativeModel('gemini-1.5-flash')
print('Vertex AI connection successful!')
"
```

## 10. Run Application

### 10.1 Process Weekly Reports
```bash
python weekly_report_processor.py
```

### 10.2 Start Web Dashboard
```bash
python app.py
```

Access at: http://localhost:5000

## Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Gmail API authentication failed**
   - Check `credentials.json` is in project root
   - Ensure OAuth consent screen is configured
   - Add your email as test user

3. **Vertex AI authentication failed**
   - Check `vertex-key.json` is in project root
   - Verify service account has "Vertex AI User" role
   - Confirm GOOGLE_CLOUD_PROJECT_ID environment variable

4. **Permission denied errors**
   - Check file permissions on credential files
   - Ensure virtual environment is activated

5. **Port 5000 already in use**
   ```bash
   # Use different port
   python app.py --port 8080
   ```

### Debug Mode

Run with debug information:
```bash
# Enable debug logging
export FLASK_DEBUG=1
python app.py
```

## Security Checklist

- [ ] `credentials.json` and `vertex-key.json` are in `.gitignore`
- [ ] Environment variables are set (not hardcoded)
- [ ] File permissions are restrictive (600) for credential files
- [ ] OAuth consent screen is properly configured
- [ ] Service account has minimal required permissions

## Next Steps

1. Configure master data lists in `weekly_report_processor.py`
2. Customize AI prompts for your report format
3. Set up automated processing (cron jobs, etc.)
4. Consider deployment to cloud platform

For deployment instructions, see individual deployment guides:
- [Docker Deployment](README_DEPLOY.md#docker)
- [Heroku Deployment](README_DEPLOY.md#heroku)
- [AWS Deployment](README_DEPLOY.md#aws)