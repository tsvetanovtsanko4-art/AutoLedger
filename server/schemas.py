import re
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .models import DriveType, FuelType, InsuranceType, TransmissionType

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip()
        if not EMAIL_PATTERN.match(v):
            raise ValueError("Please enter a valid email address (e.g. you@example.com).")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("Password is required.")
        if re.search(r"\s", v):
            raise ValueError("Password must not contain spaces.")
        return v


class UserOut(ORMModel):
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ValidityPeriod(BaseModel):
    renewed_date: date
    expiry_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.expiry_date < self.renewed_date:
            raise ValueError("expiry_date must not be before renewed_date")
        return self


class InsuranceCreate(ValidityPeriod):
    type: InsuranceType


class Insurance(InsuranceCreate, ORMModel):
    id: int
    car_id: int


class InspectionCreate(ValidityPeriod):
    pass


class Inspection(InspectionCreate, ORMModel):
    id: int
    car_id: int


class ServiceCreate(BaseModel):
    date: date
    parts_list: Optional[List[str]] = []
    part_numbers: Optional[List[str]] = []
    next_service_date: Optional[date] = None
    next_service_odometer: Optional[int] = Field(default=None, ge=0)


class Service(ServiceCreate, ORMModel):
    id: int
    car_id: int


class RefuelingCreate(BaseModel):
    date: date
    fuel_type: FuelType
    cost_eur: float = Field(gt=0)
    quantity_liters: Optional[float] = Field(default=None, gt=0)
    odometer: int = Field(ge=0)


class Refueling(RefuelingCreate, ORMModel):
    id: int
    car_id: int


class VignetteCreate(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    date_start: date
    date_end: date
    price: Optional[float] = Field(default=None, ge=0)
    currency: str = "EUR"
    status: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_class: Optional[str] = None

    @field_validator("country_code")
    @classmethod
    def upper_country(cls, v: str) -> str:
        return v.upper()

    @model_validator(mode="after")
    def check_dates(self):
        if self.date_end < self.date_start:
            raise ValueError("date_end must not be before date_start")
        return self


class Vignette(VignetteCreate, ORMModel):
    id: int
    car_id: int


def normalize_identifier(v: Optional[str]) -> Optional[str]:
    # Plates and VINs are unique regardless of case, so they are stored upper-case.
    if v is None:
        return None
    v = v.strip().upper()
    if not v:
        raise ValueError("must not be empty")
    return v


class CarCreate(BaseModel):
    plate: str
    make: str = Field(min_length=1)
    model: str = Field(min_length=1)
    model_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    current_odometer: int = Field(default=0, ge=0)
    vin: Optional[str] = None
    engine_model: Optional[str] = None
    engine_volume: Optional[float] = Field(default=None, ge=0)
    transmission: Optional[TransmissionType] = None
    drive_type: Optional[DriveType] = None
    tire_size: Optional[str] = None

    _normalize = field_validator("plate", "vin")(normalize_identifier)


class CarUpdate(BaseModel):
    plate: Optional[str] = None
    make: Optional[str] = Field(default=None, min_length=1)
    model: Optional[str] = Field(default=None, min_length=1)
    model_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    current_odometer: Optional[int] = Field(default=None, ge=0)
    engine_model: Optional[str] = None
    engine_volume: Optional[float] = Field(default=None, ge=0)
    transmission: Optional[TransmissionType] = None
    drive_type: Optional[DriveType] = None
    tire_size: Optional[str] = None
    is_favorite: Optional[bool] = None

    _normalize = field_validator("plate")(normalize_identifier)


class Car(ORMModel):
    # Response model: no input constraints, so older rows always serialize.
    id: int
    user_id: int
    plate: str
    make: str
    model: str
    model_year: Optional[int] = None
    current_odometer: int
    vin: Optional[str] = None
    engine_model: Optional[str] = None
    engine_volume: Optional[float] = None
    transmission: Optional[TransmissionType] = None
    drive_type: Optional[DriveType] = None
    tire_size: Optional[str] = None
    is_favorite: bool
    insurances: List[Insurance] = []
    inspections: List[Inspection] = []
    services: List[Service] = []
    refuelings: List[Refueling] = []
    vignettes: List[Vignette] = []
