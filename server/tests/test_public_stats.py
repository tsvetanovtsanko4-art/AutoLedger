from .conftest import refuel


def test_stats_on_empty_database(client):
    resp = client.get("/api/public/stats")

    assert resp.status_code == 200
    assert resp.json() == {
        "cars_by_make": [],
        "cost_by_year": [],
        "consumption_by_model": [],
        "consumption_by_car": [],
    }


def test_stats_aggregate_refuelings(client, auth_headers, car):
    refuel(client, auth_headers, car["id"], 1000, cost=60)
    refuel(client, auth_headers, car["id"], 1500, liters=35, cost=70)

    stats = client.get("/api/public/stats").json()

    assert stats["cars_by_make"] == [{"make": "VW", "count": 1}]
    assert stats["cost_by_year"] == [{"year": 2026, "total_eur": 130.0}]
    assert stats["consumption_by_model"] == [
        {"make": "VW", "model": "Golf", "avg_l_per_100km": 7.0, "sample_count": 1}
    ]
    assert stats["consumption_by_car"][0]["avg_cost_per_km"] == 0.26


def test_stats_are_cached(client, auth_headers, car):
    client.get("/api/public/stats")
    client.post("/api/cars", json={"plate": "CB2222BB", "make": "Skoda", "model": "Octavia"}, headers=auth_headers)

    makes = [row["make"] for row in client.get("/api/public/stats").json()["cars_by_make"]]

    assert makes == ["VW"]
