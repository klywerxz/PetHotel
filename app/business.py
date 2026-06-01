from sqlalchemy.orm import Session
from app.models import Booking
from datetime import date

def check_availability(db: Session, start_date: date, end_date: date, exclude_booking_id: int = None) -> bool:
    query = db.query(Booking).filter(
        Booking.status.in_(["confirmed", "active"]),
        Booking.start_date <= end_date,
        Booking.end_date >= start_date
    )
    if exclude_booking_id:
        query = query.filter(Booking.booking_id != exclude_booking_id)
    occupied = query.count()
    total_places = 10
    return occupied < total_places

def calculate_booking_total(db: Session, booking_id: int) -> float:
    from app.models import BookingService
    services = db.query(BookingService).filter(BookingService.booking_id == booking_id).all()
    return sum(s.amount for s in services) if services else 0.0

def get_free_places(db: Session, target_date: date) -> int:
    occupied = db.query(Booking).filter(
        Booking.status.in_(["confirmed", "active"]),
        Booking.start_date <= target_date,
        Booking.end_date >= target_date
    ).count()
    return 10 - occupied