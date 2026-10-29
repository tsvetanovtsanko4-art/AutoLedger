"""Fill the database with realistic sample data.

    python -m server.seed                 # 1000 users, 3000 cars
    python -m server.seed --users 50 --cars 100
    python -m server.seed --reset         # drop all tables first

Every user's password is `password123`. Besides demo@example.com, users are
named user1@autoledger.test, user2@autoledger.test, ... which the load tests rely on.
"""

import argparse
import random
from datetime import date, timedelta

from sqlalchemy import select

from . import models
from .auth import hash_password
from .database import SessionLocal, engine

PASSWORD = "password123"
DEMO_USERS = ["demo@example.com", "user@example.com", "admin@example.com"]
PLATE_REGIONS = ["CA", "CB", "PB", "B", "KH", "BT", "CT", "TX", "E", "M", "OB", "VT", "H", "P", "C"]
PLATE_LETTERS = "ABEKMHOPCTYX"  # letters that look the same in Latin and Cyrillic

# (model, engine, litres, year, transmission, drive, fuel)
CATALOG = {
    "Toyota": [
        ("Corolla", "1.8 Hybrid", 1.8, 2019, "CVT", "FWD", "PETROL"),
        ("RAV4", "2.5 Hybrid", 2.5, 2021, "CVT", "AWD", "PETROL"),
        ("Yaris", "1.5 VVT-i", 1.5, 2018, "MANUAL", "FWD", "PETROL"),
        ("Land Cruiser", "3.0 D-4D", 3.0, 2017, "AUTOMATIC", "AWD", "DIESEL"),
    ],
    "Subaru": [
        ("Outback", "2.5 Boxer", 2.5, 2017, "CVT", "AWD", "PETROL"),
        ("Forester", "2.0 Boxer", 2.0, 2020, "CVT", "AWD", "PETROL"),
    ],
    "Dacia": [
        ("Duster", "1.5 dCi", 1.5, 2018, "MANUAL", "AWD", "DIESEL"),
        ("Sandero", "1.0 TCe", 1.0, 2021, "MANUAL", "FWD", "PETROL"),
        ("Logan", "1.6 MPI", 1.6, 2015, "MANUAL", "FWD", "PETROL"),
    ],
    "VW": [
        ("Golf VII", "2.0 TDI", 2.0, 2016, "DCT", "FWD", "DIESEL"),
        ("Passat", "2.0 TDI", 2.0, 2019, "DCT", "FWD", "DIESEL"),
        ("Tiguan", "2.0 TSI", 2.0, 2020, "DCT", "AWD", "PETROL"),
        ("Polo", "1.0 TSI", 1.0, 2021, "AUTOMATIC", "FWD", "PETROL"),
    ],
    "Audi": [
        ("A4", "2.0 TDI", 2.0, 2017, "DCT", "AWD", "DIESEL"),
        ("Q5", "3.0 TDI", 3.0, 2018, "AUTOMATIC", "AWD", "DIESEL"),
        ("A3", "1.5 TFSI", 1.5, 2020, "DCT", "FWD", "PETROL"),
    ],
    "BMW": [
        ("320d", "2.0 Diesel", 2.0, 2015, "AUTOMATIC", "RWD", "DIESEL"),
        ("X5", "3.0d", 3.0, 2019, "AUTOMATIC", "AWD", "DIESEL"),
        ("116i", "1.5 Petrol", 1.5, 2016, "MANUAL", "RWD", "PETROL"),
    ],
    "Skoda": [
        ("Octavia", "1.6 TDI", 1.6, 2018, "MANUAL", "FWD", "DIESEL"),
        ("Superb", "2.0 TDI", 2.0, 2020, "DCT", "AWD", "DIESEL"),
        ("Fabia", "1.0 MPI", 1.0, 2019, "MANUAL", "FWD", "PETROL"),
    ],
    "Mercedes": [
        ("C220d", "2.0 Diesel", 2.0, 2019, "AUTOMATIC", "RWD", "DIESEL"),
        ("A200", "1.4 Petrol", 1.4, 2021, "DCT", "FWD", "PETROL"),
    ],
    "Ford": [
        ("Focus", "1.5 EcoBoost", 1.5, 2018, "MANUAL", "FWD", "PETROL"),
        ("Kuga", "1.5 EcoBlue", 1.5, 2020, "AUTOMATIC", "AWD", "DIESEL"),
    ],
    "Renault": [
        ("Megane", "1.5 dCi", 1.5, 2018, "MANUAL", "FWD", "DIESEL"),
        ("Clio", "1.0 TCe", 1.0, 2020, "MANUAL", "FWD", "PETROL"),
    ],
    "Hyundai": [
        ("Tucson", "1.6 T-GDi", 1.6, 2021, "DCT", "AWD", "PETROL"),
        ("i30", "1.5 T-GDi", 1.5, 2020, "MANUAL", "FWD", "PETROL"),
    ],
}
SPECS = [(make, *spec) for make, specs in CATALOG.items() for spec in specs]

SERVICE_JOBS = [
    ["Oil Change", "Oil Filter"],
    ["Oil Change", "Air Filter", "Cabin Filter"],
    ["Brake Pads Front"],
    ["Oil Change", "Spark Plugs"],
    ["Timing Belt", "Water Pump"],
]


def consumption_range(litres: float, fuel: str) -> tuple[float, float]:
    """Typical real-world L/100km for an engine size."""
    if fuel == "DIESEL":
        if litres <= 1.6:
            return 4.5, 6.0
        if litres <= 2.0:
            return 5.5, 7.0
        return 6.5, 9.0
    if litres <= 1.0:
        return 5.5, 8.0
    if litres <= 1.5:
        return 6.5, 9.0
    if litres <= 2.0:
        return 8.0, 11.0
    if litres <= 2.5:
        return 10.0, 13.0
    return 12.0, 15.5


def tank_size(litres: float) -> float:
    for limit, tank in ((1.0, 40), (1.5, 45), (2.0, 55), (2.5, 60)):
        if litres <= limit:
            return tank
    return 70


def unique(generate, used: set) -> str:
    while (value := generate()) in used:
        pass
    used.add(value)
    return value


def random_plate() -> str:
    letters = "".join(random.choices(PLATE_LETTERS, k=2))
    return f"{random.choice(PLATE_REGIONS)}{random.randint(1000, 9999)}{letters}"


def random_vin() -> str:
    return f"W{random.choice('ABCDEFGHJ')}{random.randint(10000, 99999)}P{random.randint(100000, 999999)}"


def refuelings_for(car: models.Car, litres: float, fuel: str) -> list[models.Refueling]:
    low, high = consumption_range(litres, fuel)
    tank = tank_size(litres)
    price_low, price_high = (1.70, 1.95) if fuel == "DIESEL" else (1.80, 2.05)
    odometer = max(1000, car.current_odometer - random.randint(10_000, 120_000))
    day = date.today() - timedelta(days=730)

    records = []
    for _ in range(random.randint(4, 14)):
        quantity = round(random.uniform(tank * 0.5, tank * 0.95), 2)
        odometer = min(odometer + round(quantity / random.uniform(low, high) * 100), car.current_odometer)
        day += timedelta(days=random.randint(7, 45))
        records.append(
            models.Refueling(
                date=min(day, date.today()),
                fuel_type=models.FuelType[fuel],
                cost_eur=round(quantity * random.uniform(price_low, price_high), 2),
                quantity_liters=quantity,
                odometer=odometer,
            )
        )
    return records


def seed(user_count: int, car_count: int) -> None:
    # Hashing is the slow part, and every user shares the same password.
    password_hash = hash_password(PASSWORD)
    emails = DEMO_USERS + [f"user{i}@autoledger.test" for i in range(1, user_count - len(DEMO_USERS) + 1)]
    plates, vins = set(), set()

    with SessionLocal() as db:
        users = [models.User(email=email, hashed_password=password_hash) for email in emails]
        db.add_all(users)
        db.flush()

        for i in range(car_count):
            make, model, engine_name, litres, year, transmission, drive, fuel = random.choice(SPECS)
            car = models.Car(
                owner=users[i % len(users)],
                plate=unique(random_plate, plates),
                vin=unique(random_vin, vins),
                make=make,
                model=model,
                model_year=year,
                current_odometer=random.randint(15_000, 280_000),
                engine_model=engine_name,
                engine_volume=litres,
                transmission=models.TransmissionType[transmission],
                drive_type=models.DriveType[drive],
                is_favorite=random.random() < 0.3,
            )
            car.refuelings = refuelings_for(car, litres, fuel)
            car.services = [
                models.Service(
                    date=date.today() - timedelta(days=random.randint(30, 500)),
                    parts_list=random.choice(SERVICE_JOBS),
                    part_numbers=[],
                    next_service_odometer=car.current_odometer + random.randint(5000, 15000),
                )
            ]
            db.add(car)

        db.commit()

    print(f"Seeded {len(users)} users and {car_count} cars. Password for every user: {PASSWORD}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--users", type=int, default=1000)
    parser.add_argument("--cars", type=int, default=3000)
    parser.add_argument("--reset", action="store_true", help="drop and recreate all tables first")
    args = parser.parse_args()

    if args.reset:
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(models.User.id).limit(1)) and not args.reset:
            parser.exit(1, "The database already has users; pass --reset to start from scratch.\n")

    seed(max(args.users, len(DEMO_USERS)), args.cars)


if __name__ == "__main__":
    main()
