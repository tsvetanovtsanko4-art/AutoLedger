from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from .database import Base


class FuelType(str, enum.Enum):
    PETROL = "Petrol"
    LPG = "LPG"
    CNG = "CNG"
    DIESEL = "Diesel"
    ELECTRICITY = "Electricity"


class InsuranceType(str, enum.Enum):
    CIVIL_LIABILITY = "Civil Liability"
    CASCO = "Casco"


class TransmissionType(str, enum.Enum):
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"
    CVT = "CVT"
    DCT = "DCT"


class DriveType(str, enum.Enum):
    FWD = "FWD"
    RWD = "RWD"
    AWD = "AWD"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    cars = relationship("Car", back_populates="owner")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plate = Column(String, index=True, unique=True)
    make = Column(String)
    model = Column(String)
    model_year = Column(Integer, nullable=True)
    current_odometer = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)

    # Extended fields
    vin = Column(String, nullable=True, unique=True)
    engine_model = Column(String, nullable=True)
    engine_volume = Column(Float, nullable=True)
    transmission = Column(Enum(TransmissionType), nullable=True)
    drive_type = Column(Enum(DriveType), nullable=True)
    tire_size = Column(String, nullable=True)

    owner = relationship("User", back_populates="cars")
    insurances = relationship("Insurance", back_populates="car", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="car", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="car", cascade="all, delete-orphan")
    refuelings = relationship("Refueling", back_populates="car", cascade="all, delete-orphan")
    vignettes = relationship("Vignette", back_populates="car", cascade="all, delete-orphan")


class Insurance(Base):
    __tablename__ = "insurances"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    type = Column(Enum(InsuranceType))
    renewed_date = Column(Date)
    expiry_date = Column(Date)

    car = relationship("Car", back_populates="insurances")


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    renewed_date = Column(Date)
    expiry_date = Column(Date)

    car = relationship("Car", back_populates="inspections")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    date = Column(Date)
    parts_list = Column(JSON)
    part_numbers = Column(JSON)
    next_service_date = Column(Date, nullable=True)
    next_service_odometer = Column(Integer, nullable=True)

    car = relationship("Car", back_populates="services")


class Refueling(Base):
    __tablename__ = "refuelings"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    date = Column(Date)
    fuel_type = Column(Enum(FuelType))
    cost_eur = Column(Float)
    quantity_liters = Column(Float, nullable=True)
    odometer = Column(Integer)

    car = relationship("Car", back_populates="refuelings")


class Vignette(Base):
    __tablename__ = "vignettes"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    country_code = Column(String)
    date_start = Column(Date)
    date_end = Column(Date)
    price = Column(Float, nullable=True)
    currency = Column(String, default="EUR")
    status = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)
    vehicle_class = Column(String, nullable=True)

    car = relationship("Car", back_populates="vignettes")
