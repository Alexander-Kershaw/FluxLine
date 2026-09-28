from datetime import date
import httpx
from fluxline.ingestion.elexon.models import ElexonFuelHHResponse

"""
=========================================================================================================

ELEXON FUELHH CLIENT

=========================================================================================================

ElexonClient is the client for the Elexon FUELHH API. It has the following responsibilities:

- constucting the request to the Elexon FUELHH API, including the URL and query parameters.
- sending the request to the Elexon FUELHH API and receiving the response.
- validating the response from the Elexon FUELHH API and returning the data in a structured format.

The flow is as follows:

Python inputs -> construction of HTTP request -> sending the request -> checking HTTP response success
-> decoding the JSON response payload -> validaing the JSON response against the ElexonFuelHHResponse model
-> returning the validated data

=========================================================================================================
"""

ELEXON_FUELHH_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH"

class ElexonClient:

    def __init__(self, http_client: httpx.Client) -> None:
        self._http_client = http_client

    def fetch_fuelhh(
            self,
            settlement_date_from: date,
            settlement_date_to: date
    ) -> ElexonFuelHHResponse:

        if settlement_date_from > settlement_date_to:
            raise ValueError("settlement_date_from must be less than or equal to settlement_date_to")

        response = self._http_client.get(
            url=ELEXON_FUELHH_URL,
            params={
                "settlementDateFrom": settlement_date_from.isoformat(),
                "settlementDateTo": settlement_date_to.isoformat(),
                "format": "json"
            },
        )

        response.raise_for_status()

        return ElexonFuelHHResponse.model_validate(response.json())