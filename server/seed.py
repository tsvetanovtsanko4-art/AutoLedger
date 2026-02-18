from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import date, timedelta
import random

# Create tables
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # Check if data exists
        if db.query(models.User).first():
            print("Data already exists. Skipping seed.")
            return

        print("Seeding data...")

        # Create Users
        users = []
        for i in range(1, 4):
            user = models.User(
                email=f"user{i}@example.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW" # "secret"
            )
            db.add(user)
            users.append(user)
        db.commit()

        # Create Cars
        cars_data = [
            {"make": "Toyota", "model": "Corolla", "year": 2018, "engine": "1.8 Hybrid", "vol": 1.8},
            {"make": "Honda", "model": "Civic", "year": 2020, "engine": "1.5 Turbo", "vol": 1.5},
            {"make": "Ford", "model": "Focus", "year": 2016, "engine": "1.0 EcoBoost", "vol": 1.0},
            {"make": "BMW", "model": "320d", "year": 2019, "engine": "2.0 Diesel", "vol": 2.0},
            {"make": "Tesla", "model": "Model 3", "year": 2022, "engine": "Electric", "vol": 0.0},
        ]

        cars = []
        for i, data in enumerate(cars_data):
            owner = users[i % len(users)]
            car = models.Car(
                user_id=owner.id,
                plate=f"CB{random.randint(1000, 9999)}TX",
                make=data["make"],
                model=data["model"],
                model_year=data["year"],
                current_odometer=random.randint(10000, 150000),
                vin=f"VIN{random.randint(10000000000, 99999999999)}",
                engine_model=data["engine"],
                engine_volume=data["vol"],
                transmission=random.choice(list(models.TransmissionType)),
                drive_type=random.choice(list(models.DriveType)),
                is_favorite=i == 0
            )
            db.add(car)
            cars.append(car)
        db.commit()

        # Create Refuelings (for stats)
        for car in cars:
            if car.make == "Tesla": continue # Skip refueling for now
            
            odo = car.current_odometer - 5000
            for _ in range(5):
                odo += random.randint(400, 800)
                if odo > car.current_odometer: break
                
                refueling = models.Refueling(
                    car_id=car.id,
                    date=date.today() - timedelta(days=random.randint(1, 365)),
                    fuel_type=models.FuelType.PETROL if "Hybrid" in car.engine_model else models.FuelType.DIESEL if "Diesel" in car.engine_model else models.FuelType.PETROL,
                    cost_eur=random.uniform(50, 90),
                    odometer=odo
                )
                db.add(refueling)
        
        db.commit()
        print("Seeding complete!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
