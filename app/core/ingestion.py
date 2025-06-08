import pandas as pd
from sqlalchemy.orm import Session
from .models import StoreStatus, BusinessHours, StoreTimezone
from .database import SessionLocal, engine
from datetime import datetime
import pytz

def ingest_store_status(csv_path: str):
    print("Starting store status ingestion...")
    df = pd.read_csv(csv_path)
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
    
    session = SessionLocal()
    try:
        session.query(StoreStatus).delete()
        session.commit()
        
        batch_size = 10000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            records = []
            
            for _, row in batch_df.iterrows():
                records.append({
                    'store_id': row['store_id'],
                    'status': row['status'],
                    'timestamp_utc': row['timestamp_utc']
                })
            
            session.bulk_insert_mappings(StoreStatus, records)
            session.commit()
        
        print(f"Ingested {len(df)} store status records")
    finally:
        session.close()

def ingest_business_hours(csv_path: str):
    print("Starting business hours ingestion...")
    df = pd.read_csv(csv_path)
    df['start_time_local'] = pd.to_datetime(df['start_time_local']).dt.time
    df['end_time_local'] = pd.to_datetime(df['end_time_local']).dt.time
    
    session = SessionLocal()
    try:
        session.query(BusinessHours).delete()
        session.commit()
        
        records = []
        for _, row in df.iterrows():
            records.append({
                'store_id': row['store_id'],
                'day_of_week': row['dayOfWeek'],
                'start_time_local': row['start_time_local'],
                'end_time_local': row['end_time_local']
            })
        
        session.bulk_insert_mappings(BusinessHours, records)
        session.commit()
        print(f"Ingested {len(df)} business hours records")
    finally:
        session.close()

def ingest_timezones(csv_path: str):
    print("Starting timezones ingestion...")
    df = pd.read_csv(csv_path)
    
    session = SessionLocal()
    try:
        session.query(StoreTimezone).delete()
        session.commit()
        
        records = []
        for _, row in df.iterrows():
            records.append({
                'store_id': row['store_id'],
                'timezone_str': row['timezone_str']
            })
        
        session.bulk_insert_mappings(StoreTimezone, records)
        session.commit()
        print(f"Ingested {len(df)} timezone records")
    finally:
        session.close()

def ingest_all_data():
    ingest_timezones('data/timezones.csv')
    ingest_business_hours('data/menu_hours.csv')
    ingest_store_status('data/store_status.csv') 