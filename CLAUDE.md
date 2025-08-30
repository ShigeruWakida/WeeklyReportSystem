# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Gmail weekly report processing system that:
- Fetches emails labeled as "週報" (weekly reports) from Gmail
- Uses Google Cloud Vertex AI to analyze and extract structured information from the reports
- Stores extracted data in a SQLite database

## Key Dependencies

- Google APIs: `googleapiclient`, `google_auth_oauthlib` for Gmail access
- Google Cloud: `google.cloud.aiplatform` for Vertex AI text analysis
- SQLite for local data storage
- Required credential files:
  - `credentials.json` - Gmail API OAuth credentials
  - `vertex-key.json` - Google Cloud service account key
  - `token.pkl` - OAuth token (auto-generated)

## Architecture

The main script `weekly_report_processor.py` performs these operations:
1. Authenticates with Gmail API using OAuth2 flow
2. Retrieves emails with the "週報" label
3. For each unprocessed email:
   - Extracts subject and body text
   - Sends to Vertex AI for natural language analysis
   - Parses AI response to extract:
     - Reporter name
     - Report date
     - Multiple client visit reports containing: client name, department, contact person, accompanying employees, content
   - Stores structured data in SQLite database
   - Tracks processed email IDs in `processed_ids.json`

## Configuration

Key settings in `weekly_report_processor.py`:
- `PROJECT_ID` - Google Cloud project ID (line 15)
- `LOCATION` - Vertex AI region (line 16) 
- `EMPLOYEE_LIST` - List of employee names for matching (lines 21-22)
- Database schema defined at lines 52-64

## Database Schema

SQLite table `weekly_reports`:
- `mail_id` - Unique Gmail message ID
- `report_date` - Date of the report
- `reporter` - Person who submitted the report
- `client_name` - Client company name
- `client_department` - Client department
- `client_person` - Client contact person
- `employee_name` - Accompanying employee from company
- `content` - Meeting/visit content

## Running the Application

```bash
python weekly_report_processor.py
```

The script will:
1. Authenticate with Gmail (opens browser on first run)
2. Process emails one by one with user confirmation
3. Display processing time for each email
4. Save progress to avoid reprocessing