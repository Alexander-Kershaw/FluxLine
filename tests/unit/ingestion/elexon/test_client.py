from datetime import date
import httpx
import pytest
from pydantic import ValidationError
from fluxline.ingestion.elexon.client import ElexonClient
from fluxline.ingestion.elexon.models import ElexonFuelHHResponse


def valid_record() -> dict[str, object]:
    return {
        "dataset": "FUELHH",
        "publishTime": "2026-09-20T23:00:00Z",
        "startTime": "2026-09-20T22:30:00Z",
        "settlementDate": "2026-09-20",
        "settlementPeriod": 48,
        "fuelType": "BIOMASS",
        "generation": 2960,
    }

# first testing the correctness of the request being sent to the API
def test_fetch_fuelhh_sends_expected_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/bmrs/api/v1/datasets/FUELHH"

        assert request.url.params["settlementDateFrom"] == "2026-09-20"
        assert request.url.params["settlementDateTo"] == "2026-09-20"
        assert request.url.params["format"] == "json"

        return httpx.Response(
            status_code=200,
            json={"data": [valid_record()]},
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as http_client:
        client = ElexonClient(http_client)

        response: ElexonFuelHHResponse = client.fetch_fuelhh(
            settlement_date_from=date(2026, 9, 20),
            settlement_date_to=date(2026, 9, 20),
        )

    assert len(response.data) == 1
    assert response.data[0].fuel_type == "BIOMASS"


# Testing the invalid data range case
def test_fetch_fuelhh_rejects_invalid_date_range() -> None:
    request_made = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_made
        request_made = True

        return httpx.Response(status_code=200, json={"data": []})

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as http_client:
        client = ElexonClient(http_client)

        with pytest.raises(ValueError):
            client.fetch_fuelhh(
                settlement_date_from=date(2026, 9, 21),
                settlement_date_to=date(2026, 9, 20),
            )

    assert request_made is False

# Testing the case where the API returns an HTTP error
def test_fetch_fuelhh_raises_for_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=503,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as http_client:
        client = ElexonClient(http_client)

        with pytest.raises(httpx.HTTPStatusError):
            client.fetch_fuelhh(
                settlement_date_from=date(2026, 9, 20),
                settlement_date_to=date(2026, 9, 20),
            )

# Testing the case where the API returns a response that does not match the expected schema
def test_fetch_fuelhh_rejects_invalid_source_schema() -> None:
    invalid_record = valid_record()
    invalid_record["generation"] = "2960"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"data": [invalid_record]},
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as http_client:
        client = ElexonClient(http_client)

        with pytest.raises(ValidationError):
            client.fetch_fuelhh(
                settlement_date_from=date(2026, 9, 20),
                settlement_date_to=date(2026, 9, 20),
            )