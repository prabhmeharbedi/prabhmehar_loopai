from datetime import datetime, timedelta, time, date
from sqlalchemy.orm import Session
from .models import StoreStatus, BusinessHours, StoreTimezone
from .database import SessionLocal
import pytz
from typing import List, Dict, Tuple
import pandas as pd

def get_store_timezone(store_id: str, session: Session) -> str:
    timezone_record = session.query(StoreTimezone).filter(StoreTimezone.store_id == store_id).first()
    return timezone_record.timezone_str if timezone_record else "America/Chicago"

def get_business_hours(store_id: str, session: Session) -> Dict[int, Tuple[time, time]]:
    hours_records = session.query(BusinessHours).filter(BusinessHours.store_id == store_id).all()
    
    if not hours_records:
        return {i: (time(0, 0), time(23, 59, 59)) for i in range(7)}
    
    business_hours = {}
    for record in hours_records:
        business_hours[record.day_of_week] = (record.start_time_local, record.end_time_local)
    
    return business_hours

def get_max_timestamp(session: Session) -> datetime:
    max_timestamp = session.query(StoreStatus.timestamp_utc).order_by(StoreStatus.timestamp_utc.desc()).first()
    return max_timestamp[0] if max_timestamp else datetime.utcnow()

def convert_utc_to_local(utc_dt: datetime, timezone_str: str) -> datetime:
    utc_tz = pytz.UTC
    local_tz = pytz.timezone(timezone_str)
    utc_dt = utc_tz.localize(utc_dt) if utc_dt.tzinfo is None else utc_dt
    return utc_dt.astimezone(local_tz)

def is_within_business_hours(local_dt: datetime, business_hours: Dict[int, Tuple[time, time]]) -> bool:
    day_of_week = local_dt.weekday()
    if day_of_week not in business_hours:
        return False
    
    start_time, end_time = business_hours[day_of_week]
    current_time = local_dt.time()
    
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        return current_time >= start_time or current_time <= end_time

def get_business_hours_duration(start_dt: datetime, end_dt: datetime, business_hours: Dict[int, Tuple[time, time]], timezone_str: str) -> float:
    total_minutes = 0
    current_dt = start_dt
    
    while current_dt < end_dt:
        local_dt = convert_utc_to_local(current_dt, timezone_str)
        day_of_week = local_dt.weekday()
        
        if day_of_week in business_hours:
            start_time, end_time = business_hours[day_of_week]
            
            day_start = local_dt.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second, microsecond=0)
            day_end = local_dt.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second, microsecond=0)
            
            if start_time > end_time:
                if local_dt.time() >= start_time:
                    day_end = day_end + timedelta(days=1)
                else:
                    day_start = day_start - timedelta(days=1)
            
            period_start = max(current_dt, day_start.astimezone(pytz.UTC).replace(tzinfo=None))
            period_end = min(end_dt, day_end.astimezone(pytz.UTC).replace(tzinfo=None))
            
            if period_start < period_end:
                total_minutes += (period_end - period_start).total_seconds() / 60
        
        current_dt = current_dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return total_minutes

def interpolate_status(observations: List[Tuple[datetime, str]], start_time: datetime, end_time: datetime) -> Tuple[float, float]:
    if not observations:
        return 0.0, 0.0
    
    observations.sort(key=lambda x: x[0])
    
    total_duration = (end_time - start_time).total_seconds() / 60
    uptime_minutes = 0.0
    
    for i in range(len(observations)):
        current_time, current_status = observations[i]
        
        if i == 0:
            segment_start = start_time
        else:
            segment_start = observations[i-1][0]
        
        if i == len(observations) - 1:
            segment_end = end_time
        else:
            segment_end = observations[i][0]
        
        segment_duration = (segment_end - segment_start).total_seconds() / 60
        
        if current_status == 'active':
            uptime_minutes += segment_duration
    
    downtime_minutes = total_duration - uptime_minutes
    return uptime_minutes, downtime_minutes

def calculate_store_metrics(store_id: str, current_time: datetime, session: Session) -> Dict[str, float]:
    timezone_str = get_store_timezone(store_id, session)
    business_hours = get_business_hours(store_id, session)
    
    hour_ago = current_time - timedelta(hours=1)
    day_ago = current_time - timedelta(days=1)
    week_ago = current_time - timedelta(weeks=1)
    
    status_records = session.query(StoreStatus).filter(
        StoreStatus.store_id == store_id,
        StoreStatus.timestamp_utc >= week_ago
    ).order_by(StoreStatus.timestamp_utc).all()
    
    observations = [(record.timestamp_utc, record.status) for record in status_records]
    
    def calculate_period_metrics(start_time: datetime, end_time: datetime) -> Tuple[float, float]:
        period_observations = [(ts, status) for ts, status in observations if start_time <= ts <= end_time]
        
        if not period_observations:
            business_duration = get_business_hours_duration(start_time, end_time, business_hours, timezone_str)
            return 0.0, business_duration
        
        filtered_observations = []
        for ts, status in period_observations:
            local_ts = convert_utc_to_local(ts, timezone_str)
            if is_within_business_hours(local_ts, business_hours):
                filtered_observations.append((ts, status))
        
        if not filtered_observations:
            business_duration = get_business_hours_duration(start_time, end_time, business_hours, timezone_str)
            return 0.0, business_duration
        
        business_duration = get_business_hours_duration(start_time, end_time, business_hours, timezone_str)
        uptime, downtime = interpolate_status(filtered_observations, start_time, end_time)
        
        scale_factor = business_duration / (uptime + downtime) if (uptime + downtime) > 0 else 0
        return uptime * scale_factor, downtime * scale_factor
    
    uptime_last_hour, downtime_last_hour = calculate_period_metrics(hour_ago, current_time)
    uptime_last_day, downtime_last_day = calculate_period_metrics(day_ago, current_time)
    uptime_last_week, downtime_last_week = calculate_period_metrics(week_ago, current_time)
    
    return {
        'store_id': store_id,
        'uptime_last_hour': uptime_last_hour,
        'uptime_last_day': uptime_last_day / 60,
        'uptime_last_week': uptime_last_week / 60,
        'downtime_last_hour': downtime_last_hour,
        'downtime_last_day': downtime_last_day / 60,
        'downtime_last_week': downtime_last_week / 60
    }

def generate_report(session: Session) -> List[Dict[str, float]]:
    current_time = get_max_timestamp(session)
    
    store_ids = session.query(StoreStatus.store_id).distinct().all()
    store_ids = [store_id[0] for store_id in store_ids]
    
    report_data = []
    for store_id in store_ids:
        metrics = calculate_store_metrics(store_id, current_time, session)
        report_data.append(metrics)
    
    return report_data 