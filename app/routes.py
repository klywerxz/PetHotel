from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, auth, business
from app.database import get_db
from app.models import User, Role
from app.auth import verify_password, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ========== АУТЕНТИФИКАЦИЯ ==========
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    from app.auth import verify_password, create_access_token
    from app.models import User, Role
    
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    access_token = create_access_token(data={"sub": user.username, "role": role.role_name})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role.role_name,
        "user_id": user.user_id
    }

# ========== КЛИЕНТЫ ==========
@router.post("/clients", response_model=schemas.ClientOut)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db, client)

@router.get("/clients", response_model=List[schemas.ClientOut])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_clients(db, skip, limit)

@router.get("/clients/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@router.put("/clients/{client_id}", response_model=schemas.ClientOut)
def update_client(client_id: int, client: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.update_client(db, client_id, client)

@router.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    crud.delete_client(db, client_id)
    return {"ok": True}

@router.get("/clients/search/")
def search_clients(q: str, db: Session = Depends(get_db)):
    return crud.search_clients(db, q)

# ========== ЖИВОТНЫЕ ==========
@router.post("/animals", response_model=schemas.AnimalOut)
def create_animal(animal: schemas.AnimalCreate, db: Session = Depends(get_db)):
    return crud.create_animal(db, animal)

@router.get("/animals/by-client/{client_id}", response_model=List[schemas.AnimalOut])
def get_animals(client_id: int, db: Session = Depends(get_db)):
    return crud.get_animals_by_client(db, client_id)

@router.delete("/animals/{animal_id}")
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    crud.delete_animal(db, animal_id)
    return {"ok": True}

# ========== БРОНИРОВАНИЯ ==========
@router.post("/bookings", response_model=schemas.BookingOut)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    if not business.check_availability(db, booking.start_date, booking.end_date):
        raise HTTPException(status_code=400, detail="Нет свободных мест")
    return crud.create_booking(db, booking)

@router.get("/bookings", response_model=List[schemas.BookingOut])
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_bookings(db, skip, limit)

@router.get("/bookings/active")
def get_active_bookings(db: Session = Depends(get_db)):
    return crud.get_active_bookings(db)

@router.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, status: str, db: Session = Depends(get_db)):
    return crud.update_booking_status(db, booking_id, status)

# ========== УСЛУГИ ==========
@router.get("/services")
def get_services(db: Session = Depends(get_db)):
    return crud.get_services(db)

# ========== ОТЧЁТЫ ==========
@router.get("/reports/income")
def income_report(db: Session = Depends(get_db)):
    from datetime import date
    return business.get_income_report(db, date(2025, 6, 1), date(2025, 6, 30))

@router.get("/reports/occupancy")
def occupancy_report(db: Session = Depends(get_db)):
    from datetime import date
    return business.get_occupancy_report(db, date.today())

# ========== ТЕСТОВЫЕ ПОЛЬЗОВАТЕЛИ ==========
def init_test_users(db: Session):
    from app.auth import get_password_hash
    
    # Проверяем, есть ли роли
    if db.query(Role).count() == 0:
        db.add(Role(role_name="admin", description="Администратор"))
        db.add(Role(role_name="manager", description="Менеджер"))
        db.add(Role(role_name="client", description="Клиент"))
        db.commit()
    
    # Создаём тестовых пользователей
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_role = db.query(Role).filter(Role.role_name == "admin").first()
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            email="admin@pet.ru",
            role_id=admin_role.role_id,
            is_active=True
        )
        db.add(admin_user)
    
    manager = db.query(User).filter(User.username == "manager").first()
    if not manager:
        manager_role = db.query(Role).filter(Role.role_name == "manager").first()
        manager_user = User(
            username="manager",
            password_hash=get_password_hash("manager123"),
            email="manager@pet.ru",
            role_id=manager_role.role_id,
            is_active=True
        )
        db.add(manager_user)
    
    client = db.query(User).filter(User.username == "client").first()
    if not client:
        client_role = db.query(Role).filter(Role.role_name == "client").first()
        client_user = User(
            username="client",
            password_hash=get_password_hash("client123"),
            email="client@pet.ru",
            role_id=client_role.role_id,
            is_active=True
        )
        db.add(client_user)
    
    db.commit()