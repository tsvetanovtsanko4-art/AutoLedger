import sys
import os
import random
import uuid
from datetime import date, timedelta

sys.path.append(os.path.join(os.getcwd(), 'server'))

from server.database import Base, engine, SessionLocal
from server import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_bulgarian_plate(used: set) -> str:
    regions = ["CA", "CB", "PB", "B", "KH", "BT", "CT", "TX", "E", "M", "OB", "VT", "H", "P", "C"]
    for _ in range(1000):
        region = random.choice(regions)
        numbers = f"{random.randint(1000, 9999)}"
        letters = "".join(random.choices("ABEKMHOPCTYX", k=2))
        plate = f"{region}{numbers}{letters}"
        if plate not in used:
            used.add(plate)
            return plate
    raise RuntimeError("Could not generate unique plate")

def unique_vin(used: set) -> str:
    for _ in range(1000):
        vin = f"W{random.choice('ABCDEFGHJ')}{random.randint(10000,99999)}P{random.randint(100000,999999)}"
        if vin not in used:
            used.add(vin)
            return vin
    raise RuntimeError("Could not generate unique VIN")

# Engine ccm -> realistic fuel consumption (L/100km) range
# Petrol/LPG: 1000ccm->6-8, 1500ccm->7-9, 2000ccm->9-11, 2500ccm->10-13, 3000ccm->12-15
# Diesel:     1600ccm->5-6, 2000ccm->5.5-7, 3000ccm->7-9

def consumption_for(engine_vol: float, fuel_type: str) -> tuple:
    """Returns (min, max) L/100km range."""
    cc = int(engine_vol * 1000)
    if "DIESEL" in fuel_type or fuel_type == "DIESEL":
        if cc <= 1600:   return (4.5, 6.0)
        elif cc <= 2000: return (5.5, 7.0)
        else:            return (6.5, 9.0)
    else:  # Petrol / LPG
        if cc <= 1000:   return (5.5, 8.0)
        elif cc <= 1500: return (6.5, 9.0)
        elif cc <= 2000: return (8.0, 11.0)
        elif cc <= 2500: return (10.0, 13.0)
        else:            return (12.0, 15.5)

def tank_size(engine_vol: float) -> float:
    """Realistic tank size based on engine volume."""
    if engine_vol <= 1.0: return 40.0
    elif engine_vol <= 1.5: return 45.0
    elif engine_vol <= 2.0: return 55.0
    elif engine_vol <= 2.5: return 60.0
    else: return 70.0

BRANDS_MODELS = {
    "Toyota": [
        {"model": "Corolla", "engine": "1.8 Hybrid", "vol": 1.8, "year": 2019, "trans": "CVT", "drive": "FWD", "fuel": "PETROL"},
        {"model": "RAV4", "engine": "2.5 Hybrid", "vol": 2.5, "year": 2021, "trans": "CVT", "drive": "AWD", "fuel": "PETROL"},
        {"model": "Yaris", "engine": "1.5 VVT-i", "vol": 1.0, "year": 2018, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Camry", "engine": "2.5 Hybrid", "vol": 2.5, "year": 2020, "trans": "CVT", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Land Cruiser", "engine": "3.0 D-4D", "vol": 3.0, "year": 2017, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "DIESEL"},
    ],
    "Subaru": [
        {"model": "Outback", "engine": "2.5 Boxer", "vol": 2.5, "year": 2017, "trans": "CVT", "drive": "AWD", "fuel": "PETROL"},
        {"model": "Forester", "engine": "2.0 Boxer", "vol": 2.0, "year": 2020, "trans": "CVT", "drive": "AWD", "fuel": "PETROL"},
        {"model": "Impreza", "engine": "2.0 Boxer", "vol": 2.0, "year": 2016, "trans": "MANUAL", "drive": "AWD", "fuel": "PETROL"},
    ],
    "Dacia": [
        {"model": "Duster", "engine": "1.5 dCi", "vol": 1.5, "year": 2018, "trans": "MANUAL", "drive": "AWD", "fuel": "DIESEL"},
        {"model": "Sandero", "engine": "1.0 TCe", "vol": 1.0, "year": 2021, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Logan", "engine": "1.6 MPI", "vol": 1.6, "year": 2015, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
    ],
    "VW": [
        {"model": "Golf VII", "engine": "2.0 TDI", "vol": 2.0, "year": 2016, "trans": "DCT", "drive": "FWD", "fuel": "DIESEL"},
        {"model": "Passat", "engine": "2.0 TDI", "vol": 2.0, "year": 2019, "trans": "DCT", "drive": "FWD", "fuel": "DIESEL"},
        {"model": "Tiguan", "engine": "2.0 TSI", "vol": 2.0, "year": 2020, "trans": "DCT", "drive": "AWD", "fuel": "PETROL"},
        {"model": "Polo", "engine": "1.0 TSI", "vol": 1.0, "year": 2021, "trans": "AUTOMATIC", "drive": "FWD", "fuel": "PETROL"},
        {"model": "T-Roc", "engine": "1.5 TSI", "vol": 1.5, "year": 2022, "trans": "DCT", "drive": "FWD", "fuel": "PETROL"},
    ],
    "Audi": [
        {"model": "A4", "engine": "2.0 TDI", "vol": 2.0, "year": 2017, "trans": "DCT", "drive": "AWD", "fuel": "DIESEL"},
        {"model": "Q5", "engine": "3.0 TDI", "vol": 3.0, "year": 2018, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "DIESEL"},
        {"model": "A3", "engine": "1.5 TFSI", "vol": 1.5, "year": 2020, "trans": "DCT", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Q3", "engine": "1.5 TFSI", "vol": 1.5, "year": 2021, "trans": "AUTOMATIC", "drive": "FWD", "fuel": "PETROL"},
    ],
    "BMW": [
        {"model": "320d", "engine": "2.0 Diesel", "vol": 2.0, "year": 2015, "trans": "AUTOMATIC", "drive": "RWD", "fuel": "DIESEL"},
        {"model": "X5", "engine": "3.0d", "vol": 3.0, "year": 2019, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "DIESEL"},
        {"model": "116i", "engine": "1.5 Petrol", "vol": 1.5, "year": 2016, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
        {"model": "X1", "engine": "2.0d", "vol": 2.0, "year": 2018, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "DIESEL"},
    ],
    "Skoda": [
        {"model": "Octavia", "engine": "1.6 TDI", "vol": 1.6, "year": 2018, "trans": "MANUAL", "drive": "FWD", "fuel": "DIESEL"},
        {"model": "Superb", "engine": "2.0 TDI", "vol": 2.0, "year": 2020, "trans": "DCT", "drive": "AWD", "fuel": "DIESEL"},
        {"model": "Fabia", "engine": "1.0 MPI", "vol": 1.0, "year": 2019, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Kodiaq", "engine": "2.0 TDI", "vol": 2.0, "year": 2021, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "DIESEL"},
    ],
    "Mercedes": [
        {"model": "C220d", "engine": "2.0 Diesel", "vol": 2.0, "year": 2019, "trans": "AUTOMATIC", "drive": "RWD", "fuel": "DIESEL"},
        {"model": "E300", "engine": "2.0 Petrol", "vol": 2.0, "year": 2018, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "PETROL"},
        {"model": "A200", "engine": "1.4 Petrol", "vol": 1.4, "year": 2021, "trans": "DCT", "drive": "FWD", "fuel": "PETROL"},
    ],
    "Ford": [
        {"model": "Focus", "engine": "1.5 EcoBoost", "vol": 1.5, "year": 2018, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Kuga", "engine": "1.5 EcoBlue", "vol": 1.5, "year": 2020, "trans": "AUTOMATIC", "drive": "AWD", "fuel": "DIESEL"},
        {"model": "Fiesta", "engine": "1.0 EcoBoost", "vol": 1.0, "year": 2019, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
    ],
    "Opel": [
        {"model": "Astra K", "engine": "1.6 CDTI", "vol": 1.6, "year": 2017, "trans": "MANUAL", "drive": "FWD", "fuel": "DIESEL"},
        {"model": "Insignia", "engine": "2.0 CDTI", "vol": 2.0, "year": 2018, "trans": "AUTOMATIC", "drive": "FWD", "fuel": "DIESEL"},
        {"model": "Crossland", "engine": "1.2 Turbo", "vol": 1.2, "year": 2021, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
    ],
    "Renault": [
        {"model": "Megane", "engine": "1.5 dCi", "vol": 1.5, "year": 2018, "trans": "MANUAL", "drive": "FWD", "fuel": "DIESEL"},
        {"model": "Clio", "engine": "1.0 TCe", "vol": 1.0, "year": 2020, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
        {"model": "Koleos", "engine": "2.0 dCi", "vol": 2.0, "year": 2019, "trans": "CVT", "drive": "AWD", "fuel": "DIESEL"},
    ],
    "Hyundai": [
        {"model": "Tucson", "engine": "1.6 T-GDi", "vol": 1.6, "year": 2021, "trans": "DCT", "drive": "AWD", "fuel": "PETROL"},
        {"model": "i30", "engine": "1.5 T-GDi", "vol": 1.5, "year": 2020, "trans": "MANUAL", "drive": "FWD", "fuel": "PETROL"},
    ],
    "Kia": [
        {"model": "Sportage", "engine": "1.6 T-GDi", "vol": 1.6, "year": 2021, "trans": "DCT", "drive": "AWD", "fuel": "PETROL"},
        {"model": "Ceed", "engine": "1.5 T-GDi", "vol": 1.5, "year": 2020, "trans": "DCT", "drive": "FWD", "fuel": "PETROL"},
    ],
}

ALL_CAR_SPECS = []
for brand, models_list in BRANDS_MODELS.items():
    for data in models_list:
        ALL_CAR_SPECS.append({"make": brand, **data})

def seed_data():
    db = SessionLocal()
    NUM_USERS = 1000
    TOTAL_CARS = 3000
    used_plates = set()
    used_vins = set()

    try:
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

        print(f"Seeding {NUM_USERS} users and {TOTAL_CARS} cars...")

        users = []
        named = [
            ("demo@example.com", "password123"),
            ("user@example.com", "password123"),
            ("admin@example.com", "password123"),
        ]
        for email, pw in named:
            u = models.User(email=email, hashed_password=hash_password(pw))
            db.add(u)
            users.append(u)
        db.commit()

        for i in range(NUM_USERS - len(named)):
            u = models.User(
                email=f"user{i+1}@autoledger.test",
                hashed_password=hash_password("password123")
            )
            db.add(u)
            users.append(u)
        db.commit()

        print(f"Created {len(users)} users.")

        cars_objs = []
        for i in range(TOTAL_CARS):
            owner = users[i % len(users)]
            spec = random.choice(ALL_CAR_SPECS)
            odometer = random.randint(15000, 280000)
            car = models.Car(
                user_id=owner.id,
                plate=get_bulgarian_plate(used_plates),
                make=spec["make"],
                model=spec["model"],
                model_year=spec["year"],
                current_odometer=odometer,
                vin=unique_vin(used_vins),
                engine_model=spec["engine"],
                engine_volume=spec["vol"],
                transmission=getattr(models.TransmissionType, spec["trans"]),
                drive_type=getattr(models.DriveType, spec["drive"]),
                is_favorite=random.choice([True, False])
            )
            db.add(car)
            cars_objs.append((car, spec))

        db.commit()
        print(f"Created {TOTAL_CARS} cars.")

        # Refuelings with realistic consumption
        for car, spec in cars_objs:
            fuel_type_str = spec["fuel"]
            fuel = getattr(models.FuelType, fuel_type_str)
            tank = tank_size(spec["vol"])
            cons_min, cons_max = consumption_for(spec["vol"], fuel_type_str)

            num_refuels = random.randint(4, 14)
            odo = max(1000, car.current_odometer - random.randint(10000, 120000))

            for _ in range(num_refuels):
                # Realistic L/100km for this engine type
                l_per_100 = random.uniform(cons_min, cons_max)
                # Simulate a realistic range fill: km driven since last fill
                qty = round(random.uniform(tank * 0.5, tank * 0.95), 2)
                km_driven = round(qty / (l_per_100 / 100))

                odo = min(odo + km_driven, car.current_odometer)

                # Price: diesel ~1.75, petrol ~1.90 per liter
                price_per_l = random.uniform(1.70, 1.95) if fuel_type_str == "DIESEL" else random.uniform(1.80, 2.05)
                cost = round(qty * price_per_l, 2)

                refueling = models.Refueling(
                    car_id=car.id,
                    date=date.today() - timedelta(days=random.randint(1, 730)),
                    fuel_type=fuel,
                    cost_eur=cost,
                    quantity_liters=qty,
                    odometer=odo
                )
                db.add(refueling)

            # Service
            service = models.Service(
                car_id=car.id,
                date=date.today() - timedelta(days=random.randint(30, 500)),
                parts_list=random.choice([
                    ["Oil Change", "Oil Filter"],
                    ["Oil Change", "Air Filter", "Cabin Filter"],
                    ["Brake Pads Front"],
                    ["Oil Change", "Spark Plugs"],
                    ["Timing Belt", "Water Pump"],
                ]),
                next_service_odometer=car.current_odometer + random.randint(5000, 15000)
            )
            db.add(service)

        db.commit()
        print("Seeding complete!")
        print("Login credentials:")
        for email, pw in named:
            print(f"  {email} / {pw}")
        print(f"  user1@autoledger.test ... user997@autoledger.test / password123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
