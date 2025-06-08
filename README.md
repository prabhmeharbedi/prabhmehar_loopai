# Store Monitoring System - Loop AI Assignment

A backend API system for monitoring restaurant store uptime/downtime with timezone-aware calculations and business hours filtering.

## Features

- **Data Ingestion**: Bulk processing of 1.85M+ status records from CSV files
- **Timezone Support**: Accurate UTC to local time conversion for 4.5K stores
- **Business Hours Filtering**: Calculations only during operating hours
- **Trigger + Poll Architecture**: Background report generation with status tracking
- **CSV Export**: Downloadable reports with required schema

## Database Schema

- **store_status**: 1.85M records (store_id, status, timestamp_utc)
- **business_hours**: 35K records (store_id, day_of_week, start/end times)
- **store_timezones**: 4.5K records (store_id, timezone_str)
- **report_status**: Report tracking (report_id, status, timestamps)

## 🛠️ Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# API will be available at http://localhost:8000
```

## API Endpoints

### POST /trigger_report
Triggers background report generation.

**Response:**
```json
{"report_id": "uuid-string"}
```

### GET /get_report?report_id={id}
Polls report status or downloads CSV.

**Responses:**
- Running: `{"status": "Running"}`
- Complete: CSV file download

## Sample Report Output

The system generates CSV reports with the following schema:
```
store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
```

Sample CSV output: [store_report_sample.csv](./store_report_sample.csv)

## Architecture

```
API Layer (FastAPI)
├── Report Service (Threading)
├── Calculator (Business Logic)
├── Database (SQLAlchemy + SQLite)
└── Data Ingestion (Pandas)
```


## Algorithm Details

### Business Hours Calculation
1. Convert UTC timestamps to local timezone
2. Check if time falls within store's operating hours
3. Handle overnight operations (start_time > end_time)
4. Default to 24/7 if no business hours defined

## key Points

- Uses latest timestamp in data as "current time" reference
- Handles missing timezone data (defaults to America/Chicago)
- Handles missing business hours (defaults to 24/7 operation)