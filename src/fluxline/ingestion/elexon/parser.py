import json

from fluxline.ingestion.elexon.models import ElexonFuelHHResponse

"""
============================================================================================================
HTTP parser
============================================================================================================

The function parse_fuelhh_response() takes a raw Elexon FuelHH HTTP response body (in bytes)
decodes it from JSON and validates it against the ElexonFuelHHResponse pydantic model.

It is seperate from the HTTP client code to keep the HTTP client focused on making requests and
receiving responses, and to keep the parsing and validation logic seperate.

Later on, I can test malformed JSON payloads without testing HTTP and do replays of a raw file through the
parser without making HTTP requests to Elexon.

============================================================================================================
"""

def parse_fuelhh_response(json_body: bytes) -> ElexonFuelHHResponse:

    response_payload = json.loads(json_body)

    return ElexonFuelHHResponse.model_validate(response_payload)