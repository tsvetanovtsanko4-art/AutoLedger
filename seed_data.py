import sys
import os

# Add the server directory to the python path
sys.path.append(os.path.join(os.getcwd(), 'server'))

# We need to use absolute imports here because we are modifying sys.path 
# and running this script directly, not as a module of the package.
# However, the server files now use relative imports, so we need to trick them 
# or import them as top-level modules if sys.path is correct.
# Actually, since we appended 'server', we can import 'database' directly if we want,
# BUT 'database.py' inside server might rely on relative imports if we change it.
# Let's try running this script as a module from root: `python -m seed_data`? 
# No, `seed_data.py` is in root.

# If we run `python seed_data.py` from root:
# sys.path has root.
# `from server.database import ...` works.
# Inside `server/database.py`, if it has relative imports, it might fail if not loaded as package.
# But `server/models.py` has `from .database import Base`.
# This requires `models` to be loaded as part of a package.
# So we should probably run this script using `python -m seed_data` is tricky if it's in root.
# Better approach: Move seed_data.py to root (it is), and script content:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.database import Base, engine, SessionLocal
from server import models
# from server.auth import hash_password # Importing this might be problematic without full app context
from passlib.context import CryptContext
from datetime import date, timedelta
import random

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_bulgarian_plate():
    # Codes: CA (Sofia), CB (Sofia), C (Sofia), PB (Plovdiv), B (Varna), KH (Kyustendil), BT (Veliko Tarnovo)
    regions = ["CA", "CB", "PB", "B", "KH", "BT", "CT", "TX"]
    region = random.choice(regions)
    numbers = f"{random.randint(1000, 9999)}"
    letters = "".join(random.choices("ABEKMHOPCTYX", k=2)) # Standard cyrillic-looking latin letters used in plates
    return f"{region} {numbers} {letters}"

def seed_data():
    db = SessionLocal()
    try:
        # Re-create tables
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

        print("Seeding data with Bulgarian cars...")

        # Create Users
        users = []
        user_emails = ["demo@example.com", "user@example.com", "admin@example.com"]
        for email in user_emails:
            user = models.User(
                email=email,
                hashed_password=hash_password("password123")
            )
            db.add(user)
            users.append(user)
        db.commit()

        # Car Data
        brands_models = {
            "Toyota": [
                {"model": "Corolla", "engine": "1.8 Hybrid", "vol": 1.8, "year": 2019, "trans": "CVT", "drive": "FWD"},
                {"model": "RAV4", "engine": "2.5 Hybrid", "vol": 2.5, "year": 2021, "trans": "CVT", "drive": "AWD"},
                {"model": "Yaris", "engine": "1.5 VVT-i", "vol": 1.5, "year": 2018, "trans": "MANUAL", "drive": "FWD"}
            ],
            "Subaru": [
                {"model": "Outback", "engine": "2.5 Boxer", "vol": 2.5, "year": 2017, "trans": "CVT", "drive": "AWD"},
                {"model": "Forester", "engine": "2.0 Boxer", "vol": 2.0, "year": 2020, "trans": "CVT", "drive": "AWD"}
            ],
            "Dacia": [
                {"model": "Duster", "engine": "1.5 dCi", "vol": 1.5, "year": 2018, "trans": "MANUAL", "drive": "AWD"},
                {"model": "Sandero", "engine": "1.0 TCe", "vol": 1.0, "year": 2021, "trans": "MANUAL", "drive": "FWD"}
            ],
            "VW": [
                {"model": "Golf VII", "engine": "2.0 TDI", "vol": 2.0, "year": 2016, "trans": "DCT", "drive": "FWD"},
                {"model": "Passat", "engine": "2.0 TDI", "vol": 2.0, "year": 2019, "trans": "DCT", "drive": "FWD"},
                {"model": "Tiguan", "engine": "2.0 TSI", "vol": 2.0, "year": 2020, "trans": "DCT", "drive": "AWD"}
            ],
            "Audi": [
                {"model": "A4", "engine": "2.0 TDI", "vol": 2.0, "year": 2017, "trans": "DCT", "drive": "AWD"},
                {"model": "Q5", "engine": "3.0 TDI", "vol": 3.0, "year": 2018, "trans": "AUTOMATIC", "drive": "AWD"}
            ],
            "BMW": [
                {"model": "320d", "engine": "2.0 Diesel", "vol": 2.0, "year": 2015, "trans": "AUTOMATIC", "drive": "RWD"},
                {"model": "X5", "engine": "3.0d", "vol": 3.0, "year": 2019, "trans": "AUTOMATIC", "drive": "AWD"}
            ],
            "Skoda": [
                {"model": "Octavia", "engine": "1.6 TDI", "vol": 1.6, "year": 2018, "trans": "MANUAL", "drive": "FWD"},
                {"model": "Superb", "engine": "2.0 TDI", "vol": 2.0, "year": 2020, "trans": "DCT", "drive": "AWD"}
            ]
        }

        cars = []
        for brand, models_list in brands_models.items():
            for data in models_list:
                # Randomly assign to a user
                owner = random.choice(users)
                
                car = models.Car(
                    user_id=owner.id,
                    plate=get_bulgarian_plate(),
                    make=brand,
                    model=data["model"],
                    model_year=data["year"],
                    current_odometer=random.randint(20000, 250000),
                    vin=f"W{random.choice('ABCDEF')}{random.randint(10000,99999)}P{random.randint(100000,999999)}",
                    engine_model=data["engine"],
                    engine_volume=data["vol"],
                    transmission=getattr(models.TransmissionType, data["trans"]),
                    drive_type=getattr(models.DriveType, data["drive"]),
                    is_favorite=random.choice([True, False])
                )
                db.add(car)
                cars.append(car)
        
        db.commit()

        # Create Record Data
        for car in cars:
            # Refuelings
            for _ in range(random.randint(3, 10)):
                cost = random.uniform(50, 120)
                fuel = models.FuelType.DIESEL if "TDI" in car.engine_model or "d" in car.engine_model or "dCi" in car.engine_model else models.FuelType.PETROL
                
                refueling = models.Refueling(
                    car_id=car.id,
                    date=date.today() - timedelta(days=random.randint(1, 600)),
                    fuel_type=fuel,
                    cost_eur=cost,
                    odometer=car.current_odometer - random.randint(100, 5000)
                )
                db.add(refueling)
            
            # Service
            service = models.Service(
                car_id=car.id,
                date=date.today() - timedelta(days=random.randint(30, 300)),
                parts_list=["Oil Change", "Filter Replacement"],
                next_service_odometer=car.current_odometer + 10000
            )
            db.add(service)

        db.commit()
        print(f"Seeding complete! Added {len(cars)} cars.")
        print("Login credentials: demo@example.com / password123")

    except Exception as e:
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
