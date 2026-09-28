from datetime import date, datetime, timezone
import httpx
from fluxline.ingestion.elexon.models import ElexonFuelHHResponse
from fluxline.ingestion.elexon.parser import parse_fuelhh_response
from fluxline.ingestion.http import HttpResponseSnapshot

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

    # Fetching the raw FUELHH data (as HTTP response snapshot)
    def fetch_fuelhh_raw(
            self,
            settlement_date_from: date,
            settlement_date_to: date
    ) -> HttpResponseSnapshot:

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

        return HttpResponseSnapshot(
            url=str(response.request.url),
            status_code=response.status_code,
            received_at=datetime.now(timezone.utc),
            headers=dict(response.headers),
            body=response.content
        )

    # Featching AND validating the FUELHH data
    def fetch_fuelhh(
            self,
            settlement_date_from: date,
            settlement_date_to: date
    ) -> ElexonFuelHHResponse:

        raw_response_snapshot: HttpResponseSnapshot = self.fetch_fuelhh_raw(
            settlement_date_from=settlement_date_from,
            settlement_date_to=settlement_date_to
        )

        return parse_fuelhh_response(json_body=raw_response_snapshot.body)