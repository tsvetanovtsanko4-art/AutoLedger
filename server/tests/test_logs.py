import requests

from server.routers import vignettes

from .conftest import refuel


def test_refueling_moves_car_odometer_forward(client, auth_headers, car):
    assert refuel(client, auth_headers, car["id"], 1500).status_code == 201

    assert client.get(f"/api/cars/{car['id']}", headers=auth_headers).json()["current_odometer"] == 1500


def test_refueling_below_current_mileage_is_rejected(client, auth_headers, car):
    assert refuel(client, auth_headers, car["id"], 999).status_code == 400


def test_refueling_rejects_non_positive_cost(client, auth_headers, car):
    assert refuel(client, auth_headers, car["id"], 1500, cost=-5).status_code == 422
    assert refuel(client, auth_headers, car["id"], 1500, cost=0).status_code == 422


def test_avg_consumption_uses_distance_between_refuelings(client, auth_headers, car):
    refuel(client, auth_headers, car["id"], 1000)
    refuel(client, auth_headers, car["id"], 1500, liters=30)  # 30 L over 500 km
    refuel(client, auth_headers, car["id"], 2000, liters=40)  # 40 L over 500 km

    resp = client.get(f"/api/cars/{car['id']}/avg-consumption", headers=auth_headers)

    assert resp.json() == {"avg_l_per_100km": 7.0, "sample_count": 2}


def test_avg_consumption_without_data(client, auth_headers, car):
    resp = client.get(f"/api/cars/{car['id']}/avg-consumption", headers=auth_headers)

    assert resp.json() == {"avg_l_per_100km": None, "sample_count": 0}


def test_insurance_expiry_must_follow_renewal(client, auth_headers, car):
    resp = client.post(
        f"/api/cars/{car['id']}/insurances",
        json={"type": "Casco", "renewed_date": "2026-05-01", "expiry_date": "2026-01-01"},
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_service_and_inspection_are_saved(client, auth_headers, car):
    service = client.post(
        f"/api/cars/{car['id']}/services",
        json={"date": "2026-02-01", "parts_list": ["Oil filter"], "part_numbers": ["W712"]},
        headers=auth_headers,
    )
    inspection = client.post(
        f"/api/cars/{car['id']}/inspections",
        json={"renewed_date": "2026-02-01", "expiry_date": "2027-02-01"},
        headers=auth_headers,
    )

    assert service.status_code == 201
    assert inspection.status_code == 201
    details = client.get(f"/api/cars/{car['id']}", headers=auth_headers).json()
    assert details["services"][0]["parts_list"] == ["Oil filter"]
    assert len(details["inspections"]) == 1


def test_vignette_put_updates_existing_country(client, auth_headers, car):
    url = f"/api/cars/{car['id']}/vignettes"
    first = {"country_code": "bg", "date_start": "2026-01-01", "date_end": "2026-12-31", "price": 50}
    client.put(url, json=first, headers=auth_headers)
    resp = client.put(url, json={**first, "price": 55}, headers=auth_headers)

    assert resp.status_code == 200
    vignettes = client.get(f"/api/cars/{car['id']}", headers=auth_headers).json()["vignettes"]
    assert len(vignettes) == 1
    assert vignettes[0]["country_code"] == "BG"
    assert vignettes[0]["price"] == 55


def test_vignette_end_must_follow_start(client, auth_headers, car):
    resp = client.put(
        f"/api/cars/{car['id']}/vignettes",
        json={"country_code": "BG", "date_start": "2026-12-31", "date_end": "2026-01-01"},
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_bgtoll_outage_returns_bad_gateway(client, auth_headers, monkeypatch):
    def fail(*args, **kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(vignettes.requests, "get", fail)

    assert client.get("/api/proxy/bgtoll/CA1234AB", headers=auth_headers).status_code == 502
