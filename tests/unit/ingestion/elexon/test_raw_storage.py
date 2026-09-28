import hashlib
import json
from datetime import datetime, timezone

from fluxline.ingestion.http import HttpResponseSnapshot
from fluxline.storage.raw import RawFileSink


def test_raw_sink_preserves_payload_and_metadata(tmp_path) -> None:
    body = b'{"data":[{"dataset":"FUELHH"}]}'

    response = HttpResponseSnapshot(
        url="https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH",
        status_code=200,
        received_at=datetime(2026, 9, 28, 10, 30, tzinfo=timezone.utc),
        headers={"content-type": "application/json"},
        body=body
    )

    sink = RawFileSink(tmp_path)

    artifact = sink.write(
        source="elexon",
        dataset="FUELHH",
        response=response,
    )

    assert artifact.payload_path.read_bytes() == body

    metadata = json.loads(
        artifact.metadata_path.read_text()
    )

    expected_hash = hashlib.sha256(body).hexdigest()

    assert artifact.sha256 == expected_hash

    assert metadata["source"] == "elexon"
    assert metadata["dataset"] == "FUELHH"
    assert metadata["statusCode"] == 200
    assert metadata["payloadSha256"] == expected_hash
    assert metadata["payloadBytes"] == len(body)