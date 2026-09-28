import json

import pytest
from pydantic import ValidationError

from fluxline.ingestion.elexon.models import ElexonFuelHHResponse
from fluxline.ingestion.elexon.parser import parse_fuelhh_response


def valid_record() -> dict[str, object]:
    return {
        "dataset": "FUELHH",
        "publishTime": "2026-09-20T23:00:00Z",
        "startTime": "2026-09-20T22:30:00Z",
        "settlementDate": "2026-09-20",
        "settlementPeriod": 48,
        "fuelType": "BIOMASS",
        "generation": 2960
    }


def test_valid_json_is_parsed_and_validated() -> None:
    body: bytes = json.dumps(
        {"data": [valid_record()]}
    ).encode()

    response: ElexonFuelHHResponse = parse_fuelhh_response(json_body=body)

    assert len(response.data) == 1
    assert response.data[0].fuel_type == "BIOMASS"


def test_malformed_json_is_rejected() -> None:
    body = b'{"data": ['

    with pytest.raises(expected_exception=json.JSONDecodeError):
        parse_fuelhh_response(json_body=body)


def test_valid_json_with_invalid_schema_is_rejected() -> None:
    record: dict[str, object] = valid_record()
    record["generation"] = "2960"

    body: bytes = json.dumps(
        {"data": [record]}
    ).encode()

    with pytest.raises(expected_exception=ValidationError):
        parse_fuelhh_response(json_body=body)