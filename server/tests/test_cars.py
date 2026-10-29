from .conftest import register_and_login


def add_car(client, headers, **fields):
    return client.post("/api/cars", json={"make": "Skoda", "model": "Octavia", **fields}, headers=headers)


def test_plate_and_vin_are_stored_upper_case(client, auth_headers):
    resp = add_car(client, auth_headers, plate=" ca1234ab ", vin="wvw123")

    assert resp.status_code == 201
    assert resp.json()["plate"] == "CA1234AB"
    assert resp.json()["vin"] == "WVW123"


def test_duplicate_plate_is_a_conflict(client, auth_headers, car):
    resp = add_car(client, auth_headers, plate="ca1234ab")

    assert resp.status_code == 409
    assert "Plate" in resp.json()["detail"]


def test_duplicate_vin_is_a_conflict(client, auth_headers, car):
    resp = add_car(client, auth_headers, plate="CB0000XX", vin=car["vin"].lower())

    assert resp.status_code == 409
    assert "VIN" in resp.json()["detail"]


def test_check_plate_sees_existing_car_in_any_case(client, auth_headers, car):
    assert client.get("/api/check/plate/ca1234ab", headers=auth_headers).json() == {"available": False}
    assert client.get("/api/check/plate/CB0000XX", headers=auth_headers).json() == {"available": True}


def test_check_plate_ignores_the_car_being_edited(client, auth_headers, car):
    resp = client.get(f"/api/check/plate/CA1234AB?exclude_car_id={car['id']}", headers=auth_headers)

    assert resp.json() == {"available": True}


def test_check_endpoints_require_login(client):
    assert client.get("/api/check/plate/CA1234AB").status_code == 401
    assert client.get("/api/check/vin/WVW").status_code == 401


def test_rejects_negative_odometer_and_empty_make(client, auth_headers):
    resp = add_car(client, auth_headers, plate="CB1111AA", make="", current_odometer=-1)

    assert resp.status_code == 422


def test_user_cannot_see_someone_elses_car(client, car):
    other = register_and_login(client, email="other@example.com")

    assert client.get(f"/api/cars/{car['id']}", headers=other).status_code == 404
    assert client.patch(f"/api/cars/{car['id']}", json={"make": "X"}, headers=other).status_code == 404


def test_my_cars_lists_favorite_first(client, auth_headers, car):
    second = add_car(client, auth_headers, plate="CB2222BB").json()
    client.patch(f"/api/cars/{second['id']}/favorite", headers=auth_headers)

    cars = client.get("/api/me/cars", headers=auth_headers).json()

    assert [c["id"] for c in cars] == [second["id"], car["id"]]


def test_partial_update_keeps_other_fields(client, auth_headers, car):
    resp = client.patch(f"/api/cars/{car['id']}", json={"model_year": 2015}, headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json()["model_year"] == 2015
    assert resp.json()["make"] == "VW"


def test_update_to_taken_plate_is_a_conflict(client, auth_headers, car):
    second = add_car(client, auth_headers, plate="CB2222BB").json()

    resp = client.patch(f"/api/cars/{second['id']}", json={"plate": "ca1234ab"}, headers=auth_headers)

    assert resp.status_code == 409
