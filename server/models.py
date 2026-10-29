import enum
from datetime import date
from typing import Optional

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    cars: Mapped[list["Car"]] = relationship(back_populates="owner")


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plate: Mapped[str] = mapped_column(unique=True, index=True)
    make: Mapped[str]
    model: Mapped[str]
    model_year: Mapped[Optional[int]]
    current_odometer: Mapped[int] = mapped_column(default=0)
    is_favorite: Mapped[bool] = mapped_column(default=False)
    vin: Mapped[Optional[str]] = mapped_column(unique=True)
    engine_model: Mapped[Optional[str]]
    engine_volume: Mapped[Optional[float]]
    transmission: Mapped[Optional[TransmissionType]]
    drive_type: Mapped[Optional[DriveType]]
    tire_size: Mapped[Optional[str]]

    owner: Mapped[User] = relationship(back_populates="cars")
    insurances: Mapped[list["Insurance"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    refuelings: Mapped[list["Refueling"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    vignettes: Mapped[list["Vignette"]] = relationship(back_populates="car", cascade="all, delete-orphan")


class Insurance(Base):
    __tablename__ = "insurances"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), index=True)
    type: Mapped[InsuranceType]
    renewed_date: Mapped[date]
    expiry_date: Mapped[date]

    car: Mapped[Car] = relationship(back_populates="insurances")


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), index=True)
    renewed_date: Mapped[date]
    expiry_date: Mapped[date]

    car: Mapped[Car] = relationship(back_populates="inspections")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), index=True)
    date: Mapped[date]
    parts_list: Mapped[Optional[list]] = mapped_column(JSON)
    part_numbers: Mapped[Optional[list]] = mapped_column(JSON)
    next_service_date: Mapped[Optional[date]]
    next_service_odometer: Mapped[Optional[int]]

    car: Mapped[Car] = relationship(back_populates="services")


class Refueling(Base):
    __tablename__ = "refuelings"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), index=True)
    date: Mapped[date]
    fuel_type: Mapped[FuelType]
    cost_eur: Mapped[float]
    quantity_liters: Mapped[Optional[float]]
    odometer: Mapped[int]

    car: Mapped[Car] = relationship(back_populates="refuelings")


class Vignette(Base):
    __tablename__ = "vignettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), index=True)
    country_code: Mapped[str]
    date_start: Mapped[date]
    date_end: Mapped[date]
    price: Mapped[Optional[float]]
    currency: Mapped[str] = mapped_column(default="EUR")
    status: Mapped[Optional[str]]
    vehicle_type: Mapped[Optional[str]]
    vehicle_class: Mapped[Optional[str]]

    car: Mapped[Car] = relationship(back_populates="vignettes")
