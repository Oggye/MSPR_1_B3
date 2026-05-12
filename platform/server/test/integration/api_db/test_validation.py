class TestApiValidation:
    def test_countries_reject_invalid_limit(self, client):
        response = client.get("/api/countries?limit=0")

        assert response.status_code == 422

    def test_country_stats_filter_by_passenger_range(self, client, sample_data):
        response = client.get("/api/countries/stats?min_passengers=105000&max_passengers=150000")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["country_code"] == "FR"
        assert data[0]["passengers"] == 110000.0

    def test_night_trains_reject_invalid_limit(self, client):
        response = client.get("/api/night-trains?limit=0")

        assert response.status_code == 422

    def test_night_trains_filter_by_operator_and_year(self, client, sample_data):
        response = client.get("/api/night-trains?operator_name=SNCF&year=2010")

        assert response.status_code == 200
        data = response.json()
        assert data
        assert all(item["operator_name"] == "SNCF" for item in data)
        assert all(item["year"] == 2010 for item in data)

    def test_operator_trains_not_found(self, client, sample_data):
        response = client.get("/api/night-trains/by-operator/999")

        assert response.status_code == 404
