import pytest
from pydantic import ValidationError

from fluxline.ingestion.elexon.models import (
    ElexonFuelHHRecord,
    ElexonFuelHHResponse,
)

# Valid FUELHH record for testing
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

# Test that a valid FUELHH record is accepted
def test_valid_fuelhh_record_is_accepted() -> None:
    record: ElexonFuelHHRecord = ElexonFuelHHRecord.model_validate(valid_record())

    assert record.dataset == "FUELHH"
    assert record.settlement_period == 48
    assert record.fuel_type == "BIOMASS"
    assert record.generation == 2960

# Negative generation has been observed in the source data so should accept it
def test_negative_generation_is_accepted() -> None:
    payload = valid_record()
    payload["fuelType"] = "INTEW"
    payload["generation"] = -346

    record: ElexonFuelHHRecord = ElexonFuelHHRecord.model_validate(payload)

    assert record.generation == -346

# Literal["FUELHH"] is used for the dataset field so any other value should be rejected
def test_wrong_dataset_is_rejected() -> None:
    payload = valid_record()
    payload["dataset"] = "FREQ"

    with pytest.raises(ValidationError):
        ElexonFuelHHRecord.model_validate(payload)

# generation is defined as an int in the model so any other type should be rejected
def test_string_generation_is_rejected() -> None:
    payload = valid_record()
    payload["generation"] = "2960"

    with pytest.raises(ValidationError):
        ElexonFuelHHRecord.model_validate(payload)

# Any unexpected fields should be rejected by the model 
def test_unexpected_field_is_rejected() -> None:
    payload = valid_record()
    payload["unexpectedField"] = "unexpected"

    with pytest.raises(ValidationError):
        ElexonFuelHHRecord.model_validate(payload)

# Test that a valid FUELHH response with nested records is accepted
def test_response_validates_nested_records() -> None:
    payload = {
        "data": [
            valid_record(),
            {
                **valid_record(),
                "fuelType": "CCGT",
                "generation": 5524,
            },
        ]
    }

    response: ElexonFuelHHResponse = ElexonFuelHHResponse.model_validate(payload)

    assert len(response.data) == 2
    assert response.data[0].fuel_type == "BIOMASS"
    assert response.data[1].fuel_type == "CCGT"