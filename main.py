from app.core.database import create_tables, SessionLocal
from app.core.ingestion import ingest_all_data
from app.core.models import StoreStatus
from app.api.endpoints import app
import uvicorn

def setup_database():
    create_tables()
    print("Database tables created")
    
    session = SessionLocal()
    try:
        record_count = session.query(StoreStatus).count()
        if record_count == 0:
            print("Database is empty, starting data ingestion...")
            ingest_all_data()
            print("Data ingestion completed")
        else:
            print(f"Database already contains {record_count} store status records, skipping ingestion")
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    setup_database()
    uvicorn.run(app, host="0.0.0.0", port=8000) 