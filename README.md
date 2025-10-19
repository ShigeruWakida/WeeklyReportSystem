# WeeklyReportSystem

AI-powered weekly report management system that automatically processes Gmail emails using Google Cloud Vertex AI (Gemini) and provides a web interface for data management, filtering, and analytics.

## 🚀 Features

- **Gmail Integration**: Automatic email retrieval using Gmail API
- **AI Processing**: Google Cloud Vertex AI (Gemini 1.5 Flash) for content analysis
- **Web Dashboard**: Interactive report management interface
- **Smart Filtering**: Filter by reporter, client, and product
- **Real-time Processing**: Live progress monitoring
- **Batch Operations**: Multi-report deletion and management
- **Product Name Standardization**: Automatic prefix detection (e.g., 2020 → TF-2020)

## 🏗️ Architecture

```
Gmail API ──→ AI Processing ──→ SQLite DB ──→ Flask Web App
    ↓              ↓               ↓            ↓
  OAuth2      Vertex AI      Structured     Management
  Auth        (Gemini)         Data         Dashboard
```

## 📁 Project Structure

```
WeeklyReportSystem/
├── weekly_report_processor.py  # Main email processing script
├── app.py                      # Flask web application
├── templates/
│   └── index.html             # Main dashboard template
├── static/
│   ├── css/style.css          # Styling
│   └── js/app_fixed.js        # Frontend JavaScript
├── config.example.py          # Configuration template
├── requirements.txt           # Python dependencies
└── SECURITY.md               # Security guidelines
```

## 🛠️ Setup

### Prerequisites

- Python 3.7+
- Google Cloud Project with Vertex AI enabled
- Gmail account with API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShigeruWakida/WeeklyReportSystem.git
   cd WeeklyReportSystem
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure authentication**
   - Set up Gmail API credentials (`credentials.json`)
   - Set up Vertex AI service account key (`vertex-key.json`)
   - See [SECURITY.md](SECURITY.md) for detailed instructions

4. **Set environment variables**
   ```bash
   export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
   export SECRET_KEY="your-secret-key"
   ```

## 📧 Gmail Setup

1. Create a Gmail label named "週報" (Weekly Report)
2. Apply this label to your weekly report emails
3. The system will automatically detect and process labeled emails

## 🎯 Usage

### Automated Deployment (Recommended)

The `auto_deploy.py` script automates the entire workflow from email processing to deployment package creation:

```bash
python auto_deploy.py
```

This single command will:
1. **Process weekly reports**: Fetch emails from Gmail and analyze with Vertex AI
2. **Update database**: Save structured data to SQLite
3. **Copy database**: Backup and copy to deployment directory
4. **Create ZIP package**: Generate timestamped deployment package for AWS

Output example:
```
[OK] 週報処理が正常に完了しました
[OK] データベースファイルのコピーが完了しました
[OK] デプロイパッケージ作成完了: weekly_reports_deploy_20251020_084621.zip
   ファイルサイズ: 1.90 MB
```

After running this script, simply upload the generated ZIP file to AWS Elastic Beanstalk.

### Manual Processing (Advanced)

For manual control over individual steps:

**Process Weekly Reports Only**
```bash
python weekly_report_processor.py
```

**Start Web Dashboard (Local Development)**
```bash
python app.py
```
Access at: http://localhost:5000

## 📊 Database Schema

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

## 🔧 Configuration

Master data is defined as constants in `weekly_report_processor.py`:

- **REPORTER_LIST**: List of report authors
- **EMPLOYEE_LIST**: Employee names for companion identification  
- **PRODUCT_LIST**: Product catalog for standardization

## 📱 Web Interface

### Dashboard Features
- **Report List**: Paginated view with filtering options
- **Statistics Panel**: Count summaries by reporter/client/product
- **Detail View**: Individual report display with edit capabilities
- **Batch Operations**: Multi-select deletion and management
- **Live Processing**: Real-time progress monitoring

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/reports` | GET | Retrieve filtered reports |
| `/api/reports/<id>` | PUT | Update report data |
| `/api/delete_mail_reports` | POST | Batch delete by mail |
| `/api/run_processor` | POST | Start email processing |
| `/api/process_logs` | GET | Get processing logs |

## 🔒 Security

- OAuth2 authentication for Gmail access
- Google Cloud service account authentication
- Sensitive data excluded from version control
- CORS protection for web APIs

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## 🚀 Deployment

Multiple deployment options available:

- **Docker**: `docker-compose up`
- **Heroku**: See `Procfile`
- **AWS Elastic Beanstalk**: See `.ebextensions/`
- **Serverless**: See `serverless.yml`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔍 Troubleshooting

### Common Issues

1. **Gmail API quota exceeded**: Wait for quota reset or request increase
2. **Vertex AI authentication failed**: Check service account permissions
3. **Database locked**: Ensure no concurrent access to SQLite file

### Support

For issues and questions:
- Check existing [GitHub Issues](https://github.com/ShigeruWakida/WeeklyReportSystem/issues)
- Review [SECURITY.md](SECURITY.md) for setup guidance
- Create a new issue with detailed information

---

Built with ❤️ using Flask, Google Cloud AI, and modern web technologies.