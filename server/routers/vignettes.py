from urllib.parse import quote

import requests
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from .. import models, schemas
from ..auth import CurrentUser, DbSession
from .cars import OwnedCar

router = APIRouter(prefix="/api", tags=["vignettes"])

BGTOLL_URL = "https://check.bgtoll.bg/check/vignette/plate/BG/{plate}"
# check.bgtoll.bg rejects requests that don't look like they come from its own page.
BGTOLL_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://check.bgtoll.bg/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


@router.put("/cars/{car_id}/vignettes", response_model=schemas.Vignette)
def upsert_vignette(vignette: schemas.VignetteCreate, car: OwnedCar, db: DbSession):
    # One vignette per country: buying a new one replaces the old record.
    record = db.scalar(
        select(models.Vignette).where(
            models.Vignette.car_id == car.id,
            models.Vignette.country_code == vignette.country_code,
        )
    )
    if record is None:
        record = models.Vignette(car_id=car.id)
        db.add(record)
    for key, value in vignette.model_dump().items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.get("/proxy/bgtoll/{plate}")
def check_bgtoll(plate: str, _: CurrentUser):
    url = BGTOLL_URL.format(plate=quote(plate.strip().upper()))
    try:
        response = requests.get(url, headers=BGTOLL_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        raise HTTPException(status_code=502, detail="BG Toll service is unavailable")
