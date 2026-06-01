from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models
from app.routes import router
import os

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet Hotel API", version="1.0")

app.include_router(router, prefix="/api/v1")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение фронтенда
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ Фронтенд подключен из: {frontend_path}")

# ========== АУТЕНТИФИКАЦИЯ ==========
from app.auth import verify_password, create_access_token, get_password_hash
from app.models import User, Role

@app.post("/api/v1/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    access_token = create_access_token(data={"sub": user.username, "role": role.role_name})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role.role_name,
        "user_id": user.user_id
    }

# ========== ОТЧЁТЫ ==========

@app.get("/api/v1/reports/income")
def income_report(db: Session = Depends(get_db)):
    try:
        from app.models import Booking, BookingService, Service
        
        results = db.query(
            Service.name,
            BookingService.amount
        ).join(
            BookingService, Service.service_id == BookingService.service_id
        ).join(
            Booking, BookingService.booking_id == Booking.booking_id
        ).all()
        
        total = sum(r.amount for r in results) if results else 0
        
        return {
            "total_income": float(total),
            "details": [{"service": r.name, "amount": float(r.amount)} for r in results]
        }
    except Exception as e:
        return {"total_income": 0, "details": [], "error": str(e)}

@app.get("/api/v1/reports/occupancy")
def occupancy_report(db: Session = Depends(get_db)):
    try:
        from datetime import date
        from app.models import Booking
        
        today = date.today()
        occupied = db.query(Booking).filter(
            Booking.status.in_(["confirmed", "active"]),
            Booking.start_date <= today,
            Booking.end_date >= today
        ).count()
        
        total_places = 10
        free_places = total_places - occupied
        percent = (occupied / total_places) * 100 if total_places > 0 else 0
        
        return {
            "date": today.isoformat(),
            "occupied": occupied,
            "total": total_places,
            "free": free_places,
            "percent": percent
        }
    except Exception as e:
        return {"date": str(date.today()), "occupied": 0, "total": 10, "free": 10, "percent": 0, "error": str(e)}

# ========== ТЕСТОВЫЕ ПОЛЬЗОВАТЕЛИ ==========
def init_test_users(db: Session):
    if db.query(Role).count() == 0:
        db.add(Role(role_name="admin", description="Администратор"))
        db.add(Role(role_name="manager", description="Менеджер"))
        db.add(Role(role_name="client", description="Клиент"))
        db.commit()
    
    if not db.query(User).filter(User.username == "admin").first():
        admin_role = db.query(Role).filter(Role.role_name == "admin").first()
        db.add(User(username="admin", password_hash=get_password_hash("admin123"), email="admin@pet.ru", role_id=admin_role.role_id))
    
    if not db.query(User).filter(User.username == "manager").first():
        manager_role = db.query(Role).filter(Role.role_name == "manager").first()
        db.add(User(username="manager", password_hash=get_password_hash("manager123"), email="manager@pet.ru", role_id=manager_role.role_id))
    
    if not db.query(User).filter(User.username == "client").first():
        client_role = db.query(Role).filter(Role.role_name == "client").first()
        db.add(User(username="client", password_hash=get_password_hash("client123"), email="client@pet.ru", role_id=client_role.role_id))
    
    db.commit()

# Запуск создания пользователей
db = next(get_db())
init_test_users(db)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)