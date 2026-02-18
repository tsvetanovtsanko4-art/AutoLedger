
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from server import models

# Source: SQLite (mounted in container)
SQLITE_URL = "sqlite:////app/car_tracker.db"

# Destination: PostgreSQL (from env)
POSTGRES_URL = os.getenv("DATABASE_URL")

def migrate():
    print("Starting migration...")
    
    if not os.path.exists("/app/car_tracker.db"):
        print("Error: /app/car_tracker.db not found. Make sure it is mounted.")
        sys.exit(1)

    # Connect to SQLite
    print(f"Connecting to Source: {SQLITE_URL}")
    sqlite_engine = create_engine(SQLITE_URL)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    source_session = SqliteSession()

    # Connect to Postgres
    print(f"Connecting to Destination: {POSTGRES_URL}")
    pg_engine = create_engine(POSTGRES_URL)
    PgSession = sessionmaker(bind=pg_engine)
    dest_session = PgSession()

    # Ensure tables exist in dest
    models.Base.metadata.create_all(bind=pg_engine)

    try:
        # 1. Users
        print("\nMigrating Users...")
        users = source_session.query(models.User).all()
        for u in users:
            existing = dest_session.query(models.User).filter_by(email=u.email).first()
            if not existing:
                print(f"  Adding user: {u.email} (ID: {u.id})")
                new_user = models.User(
                    id=u.id,
                    email=u.email,
                    hashed_password=u.hashed_password
                )
                dest_session.add(new_user)
            else:
                print(f"  Skipping existing user: {u.email}")
        dest_session.commit()
        reset_sequence(dest_session, "users")

        # 2. Cars
        print("\nMigrating Cars...")
        cars = source_session.query(models.Car).all()
        for c in cars:
            if not dest_session.query(models.Car).get(c.id):
                print(f"  Adding car: {c.make} {c.model} (ID: {c.id})")
                new_car = models.Car(
                    id=c.id,
                    user_id=c.user_id,
                    plate=c.plate,
                    make=c.make,
                    model=c.model,
                    model_year=c.model_year,
                    current_odometer=c.current_odometer,
                    is_favorite=c.is_favorite,
                    vin=c.vin,
                    engine_model=c.engine_model,
                    engine_volume=c.engine_volume,
                    transmission=c.transmission,
                    drive_type=c.drive_type,
                    tire_size=c.tire_size
                )
                dest_session.add(new_car)
        dest_session.commit()
        reset_sequence(dest_session, "cars")

        # 3. Insurances
        print("\nMigrating Insurances...")
        insurances = source_session.query(models.Insurance).all()
        for i in insurances:
             if not dest_session.query(models.Insurance).get(i.id):
                new_rec = models.Insurance(
                    id=i.id, car_id=i.car_id, type=i.type, renewed_date=i.renewed_date, expiry_date=i.expiry_date
                )
                dest_session.add(new_rec)
        dest_session.commit()
        reset_sequence(dest_session, "insurances")

        # 4. Inspections
        print("\nMigrating Inspections...")
        inspections = source_session.query(models.Inspection).all()
        for i in inspections:
             if not dest_session.query(models.Inspection).get(i.id):
                new_rec = models.Inspection(
                    id=i.id, car_id=i.car_id, renewed_date=i.renewed_date, expiry_date=i.expiry_date
                )
                dest_session.add(new_rec)
        dest_session.commit()
        reset_sequence(dest_session, "inspections")
        
        # 5. Services
        print("\nMigrating Services...")
        services = source_session.query(models.Service).all()
        for s in services:
             if not dest_session.query(models.Service).get(s.id):
                new_rec = models.Service(
                    id=s.id, car_id=s.car_id, date=s.date, parts_list=s.parts_list, part_numbers=s.part_numbers,
                    next_service_date=s.next_service_date, next_service_odometer=s.next_service_odometer
                )
                dest_session.add(new_rec)
        dest_session.commit()
        reset_sequence(dest_session, "services")

        # 6. Refuelings
        print("\nMigrating Refuelings...")
        refuelings = source_session.query(models.Refueling).all()
        for r in refuelings:
             if not dest_session.query(models.Refueling).get(r.id):
                new_rec = models.Refueling(
                    id=r.id, car_id=r.car_id, date=r.date, fuel_type=r.fuel_type, cost_eur=r.cost_eur, odometer=r.odometer
                )
                dest_session.add(new_rec)
        dest_session.commit()
        reset_sequence(dest_session, "refuelings")

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"\nError during migration: {e}")
        dest_session.rollback()
    finally:
        source_session.close()
        dest_session.close()

def reset_sequence(session, table_name):
    # Retrieve current max id. If null, use 0.
    sql = text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id), 0) + 1, false) FROM {table_name};")
    session.execute(sql)
    session.commit()

if __name__ == "__main__":
    migrate()
