# Store Monitoring System - Loop AI Assignment

A backend API system for monitoring restaurant store uptime/downtime with timezone-aware calculations and business hours filtering.

## 🚀 Features

- **Data Ingestion**: Bulk processing of 1.85M+ status records from CSV files
- **Timezone Support**: Accurate UTC to local time conversion for 4.5K stores
- **Business Hours Filtering**: Calculations only during operating hours
- **Interpolation Algorithm**: Extrapolates uptime/downtime from periodic observations
- **Trigger + Poll Architecture**: Background report generation with status tracking
- **CSV Export**: Downloadable reports with required schema

## 📊 Database Schema

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

## 📱 API Endpoints

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

## 📈 Sample Report Output

The system generates CSV reports with the following schema:
```
store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
```

Sample CSV output: [store_report_sample.csv](./store_report_sample.csv)

## 🔧 Architecture

```
API Layer (FastAPI)
├── Report Service (Threading)
├── Calculator (Business Logic)
├── Database (SQLAlchemy + SQLite)
└── Data Ingestion (Pandas)
```

## 💡 Improvement Ideas

### 1. **Performance Optimizations**
- **Database Partitioning**: Partition `store_status` table by date for faster queries
- **Caching Layer**: Redis cache for frequently accessed store configurations
- **Parallel Processing**: Multi-threading for report generation across store batches
- **Database Indexing**: Add composite indexes on (store_id, timestamp_utc)

### 2. **Scalability Enhancements**
- **PostgreSQL Migration**: Replace SQLite with PostgreSQL for production
- **Microservices**: Split into separate services (ingestion, calculation, reporting)
- **Message Queue**: Use Celery + Redis for background job processing
- **Load Balancing**: Multiple API instances behind load balancer

### 3. **Data Pipeline Improvements**
- **Streaming Ingestion**: Real-time data processing with Apache Kafka
- **Data Validation**: Pydantic models for CSV data validation
- **Error Handling**: Retry mechanisms for failed ingestions
- **Monitoring**: Observability with Prometheus/Grafana

### 4. **Business Logic Enhancements**
- **ML Prediction**: Predict potential downtime using historical patterns
- **Anomaly Detection**: Flag unusual downtime patterns
- **SLA Monitoring**: Track service level agreements per store
- **Alert System**: Real-time notifications for extended downtime

### 5. **API & Security**
- **Authentication**: JWT tokens or API keys
- **Rate Limiting**: Prevent API abuse
- **Pagination**: Handle large report responses
- **API Versioning**: Support multiple API versions
- **Input Validation**: Comprehensive request validation

### 6. **DevOps & Deployment**
- **Containerization**: Docker containers for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment
- **Health Checks**: Application health monitoring endpoints
- **Configuration Management**: Environment-based configs

### 7. **Data Analytics**
- **Time Series Database**: InfluxDB for time-series analytics
- **Dashboard**: Real-time monitoring dashboard
- **Reporting Engine**: Scheduled automated reports
- **Data Export**: Multiple export formats (JSON, Excel, PDF)

## 🧮 Algorithm Details

### Interpolation Logic
1. Sort observations by timestamp
2. For each time segment between observations:
   - Assume previous status continues until next observation
   - Filter to business hours only
   - Calculate duration based on timezone-converted times
3. Scale to total business hours for the period

### Business Hours Calculation
1. Convert UTC timestamps to local timezone
2. Check if time falls within store's operating hours
3. Handle overnight operations (start_time > end_time)
4. Default to 24/7 if no business hours defined

## 📁 Project Structure

```
prabhmehar_loopai/
├── app/
│   ├── core/           # Business logic
│   │   ├── models.py   # Database models
│   │   ├── database.py # Database configuration
│   │   ├── ingestion.py # Data ingestion
│   │   ├── calculator.py # Uptime/downtime logic
│   │   └── report_service.py # Report generation
│   └── api/
│       └── endpoints.py # API routes
├── data/               # CSV source files
├── reports/           # Generated CSV reports
├── main.py           # Application entry point
└── requirements.txt  # Dependencies
```

## 🎯 Technical Decisions

- **SQLite**: Chosen for simplicity; PostgreSQL recommended for production
- **FastAPI**: Modern Python framework with automatic OpenAPI docs
- **SQLAlchemy ORM**: Database abstraction with easy model definitions
- **Pandas**: Efficient CSV processing and data manipulation
- **Threading**: Background report generation without blocking API
- **Bulk Operations**: 10K batch size for optimal ingestion performance

## 📊 Performance Metrics

- **Data Ingestion**: 1.85M records processed in ~5 minutes
- **Report Generation**: 3.7K stores processed in ~10 seconds
- **Database Size**: 322MB for complete dataset
- **API Response**: Sub-second response for status checks

## 🔍 Testing

The system has been tested with:
- Full CSV dataset ingestion (1.85M+ records)
- Multiple concurrent report generation requests
- Timezone conversion accuracy across different zones
- Business hours filtering edge cases
- API endpoint functionality verification

## 📝 Notes

- Uses latest timestamp in data as "current time" reference
- Handles missing timezone data (defaults to America/Chicago)
- Handles missing business hours (defaults to 24/7 operation)
- Optimized for the provided static dataset structure 