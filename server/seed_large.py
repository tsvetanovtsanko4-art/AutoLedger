
import random
import string
from sqlalchemy.orm import Session
from server import models
from server.database import SessionLocal, engine

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

BRANDS = {
    "Subaru": ["Outback", "Forester", "Impreza", "XV", "Legacy"],
    "Toyota": ["Corolla", "RAV4", "Yaris", "Camry", "Land Cruiser"],
    "Nissan": ["Qashqai", "Juke", "X-Trail", "Leaf", "Micra"],
    "Mitsubishi": ["Outlander", "ASX", "Eclipse Cross", "L200", "Space Star"],
    "Audi": ["A3", "A4", "A6", "Q5", "Q7"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "1 Series"],
    "VW": ["Golf", "Passat", "Tiguan", "Polo", "Touareg"],
    "Skoda": ["Octavia", "Superb", "Kodiaq", "Karoq", "Fabia"],
    "Dacia": ["Duster", "Sandero", "Logan", "Jogger", "Spring"],
    "GWM": ["Haval H6", "Ora Cat", "Poer", "Tank 300", "Wey Coffee"]
}

ENGINE_TYPES = [
    ("2.0 Diesel", 2.0, models.FuelType.DIESEL),
    ("1.6 Petrol", 1.6, models.FuelType.PETROL),
    ("1.5 Turbo", 1.5, models.FuelType.PETROL),
    ("2.0 Hybrid", 2.0, models.FuelType.PETROL),
    ("Electric", 0.0, models.FuelType.ELECTRICITY)
]

def generate_plate():
    # Format: XX NNNN XX (Bulgarian style mostly)
    regions = ["CB", "B", "CA", "PB", "V", "TX", "EH"]
    region = random.choice(regions)
    num = random.randint(1000, 9999)
    suffix = "".join(random.choices(string.ascii_uppercase, k=2))
    return f"{region}{num}{suffix}"

def generate_vin():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=17))

def seed_large_dataset():
    db = SessionLocal()
    try:
        print("Fetching existing users...")
        users = db.query(models.User).all()
        if not users:
            print("No users found! Please run the basic migration or create a user first.")
            return
        
        print(f"Found {len(users)} users. Starting generation of 5000 cars...")
        
        cars_buffer = []
        BATCH_SIZE = 1000
        TOTAL_CARS = 5000

        for i in range(TOTAL_CARS):
            brand = random.choice(list(BRANDS.keys()))
            model = random.choice(BRANDS[brand])
            user = random.choice(users)
            
            engine_name, vol, fuel = random.choice(ENGINE_TYPES)
            year = random.randint(2010, 2025)
            
            car = models.Car(
                user_id=user.id,
                plate=generate_plate(),
                make=brand,
                model=model,
                model_year=year,
                current_odometer=random.randint(10000, 250000),
                is_favorite=random.choice([True, False, False, False]), # 25% chance
                vin=generate_vin(),
                engine_model=engine_name,
                engine_volume=vol,
                transmission=random.choice(list(models.TransmissionType)),
                drive_type=random.choice(list(models.DriveType)),
                tire_size=f"{random.choice([16, 17, 18, 19, 20])}inch"
            )
            cars_buffer.append(car)

            if len(cars_buffer) >= BATCH_SIZE:
                print(f"Saving batch {i+1}...")
                db.bulk_save_objects(cars_buffer)
                db.commit()
                cars_buffer = []

        if cars_buffer:
            print(f"Saving final batch...")
            db.bulk_save_objects(cars_buffer)
            db.commit()
            
        print("Successfully seeded 5000 cars!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_large_dataset()
