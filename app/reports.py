from sqlalchemy.orm import Session
from app.models import Booking, BookingService, Service
from datetime import date
import io

def get_income_report(db: Session, start_date: date, end_date: date):
    results = db.query(
        Service.name,
        Service.category,
        BookingService.amount
    ).join(
        BookingService, Service.service_id == BookingService.service_id
    ).join(
        Booking, BookingService.booking_id == Booking.booking_id
    ).filter(
        Booking.start_date >= start_date,
        Booking.end_date <= end_date
    ).all()
    
    total = sum(r.amount for r in results)
    return {"total_income": total, "details": [{"service": r.name, "amount": r.amount} for r in results]}

def get_occupancy_report(db: Session, target_date: date):
    occupied = db.query(Booking).filter(
        Booking.status.in_(["confirmed", "active"]),
        Booking.start_date <= target_date,
        Booking.end_date >= target_date
    ).count()
    return {"date": target_date, "occupied": occupied, "total": 10, "free": 10 - occupied, "percent": (occupied/10)*100}