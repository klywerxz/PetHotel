from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(30), unique=True, nullable=False)
    description = Column(Text)

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Client(Base):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    address = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Animal(Base):
    __tablename__ = "animals"
    animal_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"))
    name = Column(String(50), nullable=False)
    species = Column(String(30), nullable=False)
    breed = Column(String(50))
    birth_date = Column(Date)
    gender = Column(String(1), CheckConstraint("gender IN ('M', 'F')"))
    allergies = Column(Text)
    special_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Service(Base):
    __tablename__ = "services"
    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    price = Column(Numeric(10,2), nullable=False)
    is_active = Column(Boolean, default=True)

class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    animal_id = Column(Integer, ForeignKey("animals.animal_id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")
    total_amount = Column(Numeric(10,2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class BookingService(Base):
    __tablename__ = "bookings_services"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id", ondelete="CASCADE"))
    service_id = Column(Integer, ForeignKey("services.service_id"))
    quantity = Column(Integer, default=1)
    amount = Column(Numeric(10,2), nullable=False)

class Invoice(Base):
    __tablename__ = "invoices"
    invoice_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    amount = Column(Numeric(10,2), nullable=False)
    paid_amount = Column(Numeric(10,2), default=0)
    status = Column(String(20), default="unpaid")
    created_at = Column(DateTime, server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action_type = Column(String(30), nullable=False)
    table_name = Column(String(50))
    action_time = Column(DateTime, server_default=func.now())