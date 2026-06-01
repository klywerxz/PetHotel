from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class ClientCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class ClientOut(ClientCreate):
    client_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AnimalCreate(BaseModel):
    client_id: int
    name: str
    species: str
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    allergies: Optional[str] = None
    special_notes: Optional[str] = None

class AnimalOut(AnimalCreate):
    animal_id: int
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    client_id: int
    animal_id: int
    start_date: date
    end_date: date

class BookingOut(BookingCreate):
    booking_id: int
    status: str
    total_amount: float
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int