from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date

# ========== КЛИЕНТЫ ==========
def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.client_id == client_id).first()

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: int, client: schemas.ClientCreate):
    db_client = get_client(db, client_id)
    for key, value in client.dict().items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: int):
    db.query(models.Client).filter(models.Client.client_id == client_id).delete()
    db.commit()

def search_clients(db: Session, query: str):
    return db.query(models.Client).filter(
        (models.Client.last_name.contains(query)) | 
        (models.Client.phone.contains(query))
    ).all()

# ========== ЖИВОТНЫЕ ==========
def get_animals_by_client(db: Session, client_id: int):
    return db.query(models.Animal).filter(models.Animal.client_id == client_id).all()

def create_animal(db: Session, animal: schemas.AnimalCreate):
    db_animal = models.Animal(**animal.dict())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal

def delete_animal(db: Session, animal_id: int):
    db.query(models.Animal).filter(models.Animal.animal_id == animal_id).delete()
    db.commit()

# ========== БРОНИРОВАНИЯ ==========
def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).offset(skip).limit(limit).all()

def get_active_bookings(db: Session):
    today = date.today()
    return db.query(models.Booking).filter(
        models.Booking.status.in_(["confirmed", "active"]),
        models.Booking.start_date <= today,
        models.Booking.end_date >= today
    ).all()

def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict(), status="confirmed")
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def update_booking_status(db: Session, booking_id: int, status: str):
    db_booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    db_booking.status = status
    db.commit()
    return db_booking

# ========== УСЛУГИ ==========
def get_services(db: Session):
    return db.query(models.Service).all()

def create_service(db: Session, name: str, price: float):
    db_service = models.Service(name=name, price=price)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

# ========== ПОЛЬЗОВАТЕЛИ ==========
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()