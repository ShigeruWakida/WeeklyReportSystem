# API Documentation

RESTful API endpoints for WeeklyReportSystem

## Base URL
```
http://localhost:5000
```

## Authentication
No authentication required for local deployment. For production, implement appropriate authentication mechanisms.

## Content Types
- Request: `application/json`
- Response: `application/json`

---

## Reports API

### Get Reports
Retrieve weekly reports with optional filtering and pagination.

**Endpoint:** `GET /api/reports`

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| page | integer | Page number | 1 |
| per_page | integer | Items per page (max 100) | 10 |
| reporter | string | Filter by reporter name | - |
| client | string | Filter by client name | - |
| product | string | Filter by product name | - |

**Example Request:**
```bash
curl "http://localhost:5000/api/reports?page=1&per_page=20&reporter=西田"
```

**Response:**
```json
{
  "reports": [
    {
      "id": 1,
      "mail_id": "abc123",
      "report_date": "2024-01-15",
      "reporter": "西田",
      "client_name": "トヨタ自動車",
      "client_department": "開発部",
      "client_person": "田中課長",
      "employee_name": "藤原",
      "product_name": "TF-4060",
      "content": "案件の詳細内容..."
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

### Update Report
Update an existing weekly report.

**Endpoint:** `PUT /api/reports/<id>`

**Request Body:**
```json
{
  "reporter": "西田",
  "client_name": "トヨタ自動車",
  "client_department": "開発部",
  "client_person": "田中課長",
  "employee_name": "藤原",
  "product_name": "TF-4060",
  "content": "更新された内容"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report updated successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Report not found"
}
```

### Delete Mail Reports
Delete all reports associated with a specific mail ID.

**Endpoint:** `POST /api/delete_mail_reports`

**Request Body:**
```json
{
  "mail_id": "abc123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "3 reports deleted successfully"
}
```

---

## Master Data API

### Get Reporters
Retrieve list of unique reporters.

**Endpoint:** `GET /api/reporters`

**Response:**
```json
{
  "reporters": [
    {"name": "西田", "count": 45},
    {"name": "村田", "count": 32},
    {"name": "田村", "count": 28}
  ]
}
```

### Get Clients
Retrieve list of unique clients.

**Endpoint:** `GET /api/clients`

**Response:**
```json
{
  "clients": [
    {"name": "トヨタ自動車", "count": 15},
    {"name": "ホンダ", "count": 8},
    {"name": "日産自動車", "count": 12}
  ]
}
```

### Get Products
Retrieve list of unique products (comma-separated products are split).

**Endpoint:** `GET /api/products`

**Response:**
```json
{
  "products": [
    {"name": "TF-4060", "count": 25},
    {"name": "TF-3040", "count": 18},
    {"name": "HapLog", "count": 10}
  ]
}
```

---

## Statistics API

### Get Statistics
Retrieve summary statistics.

**Endpoint:** `GET /api/stats`

**Response:**
```json
{
  "total_reports": 150,
  "unique_reporters": 7,
  "unique_clients": 25,
  "unique_products": 15,
  "date_range": {
    "earliest": "2024-01-01",
    "latest": "2024-03-15"
  }
}
```

---

## Processing API

### Run Processor
Start the weekly report processing job.

**Endpoint:** `POST /api/run_processor`

**Response:**
```json
{
  "success": true,
  "message": "Processing started",
  "process_id": "abc123"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Processor is already running"
}
```

### Get Process Status
Check the status of the processing job.

**Endpoint:** `GET /api/process_status`

**Response:**
```json
{
  "running": true,
  "process_id": "abc123",
  "start_time": "2024-01-15T10:30:00Z"
}
```

### Get Process Logs
Retrieve processing logs in real-time.

**Endpoint:** `GET /api/process_logs`

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| lines | integer | Number of recent lines | 50 |

**Response:**
```json
{
  "logs": [
    "2024-01-15 10:30:15 - Processing started...",
    "2024-01-15 10:30:16 - Found 5 new emails",
    "2024-01-15 10:30:18 - Processed mail ID: xyz789"
  ],
  "timestamp": "2024-01-15T10:30:20Z"
}
```

---

## Utility API

### Clear Processed IDs
Clear the list of processed email IDs (allows reprocessing).

**Endpoint:** `POST /api/clear_processed`

**Response:**
```json
{
  "success": true,
  "message": "Processed IDs cleared"
}
```

### Health Check
Check API health status.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Error Responses

All API endpoints return consistent error formats:

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

### Error Format
```json
{
  "success": false,
  "message": "Detailed error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, implement appropriate rate limiting based on your requirements.

## CORS

CORS is enabled for all origins in development. For production, configure appropriate CORS settings in `app.py`.

## Examples

### Python Example
```python
import requests

# Get reports
response = requests.get('http://localhost:5000/api/reports', 
                       params={'reporter': '西田', 'page': 1})
data = response.json()

# Update report
update_data = {
    'reporter': '西田',
    'client_name': '更新されたクライアント名'
}
response = requests.put(f'http://localhost:5000/api/reports/{report_id}', 
                       json=update_data)
```

### JavaScript Example
```javascript
// Get reports with fetch
const response = await fetch('/api/reports?page=1&per_page=20');
const data = await response.json();

// Update report
const updateResponse = await fetch(`/api/reports/${reportId}`, {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        reporter: '西田',
        client_name: '更新されたクライアント名'
    })
});
```