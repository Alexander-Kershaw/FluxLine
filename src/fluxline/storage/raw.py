import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fluxline.ingestion.http import HttpResponseSnapshot

"""
============================================================================================================
RAW STORAGE (LOCAL)
============================================================================================================

This script is to accommodate raw local storage of the Elexon FUELHH payloads

Notes:

- The SHA256 hashing here is not for SCD, it is hashing the complete raw HTTP payload. This gives a 
fingerprint for the content of the payload. Therefore, if two raw responses have the same SHA256, then this
is very strong evidence that their bytes are identical (this is useful for data integrity, duplicate 
investigations, replay verification and data provenance). Note I am not doing deduplication in the raw 
data landing zone.

- The resulting directory structure looks like this:

        data/
        └── raw/
            └── elexon/
                └── FUELHH/
                    └── ingestion_date=2026-09-28/
                        ├── 20260928T103012123456Z_a97b42....json
                        └── 20260928T103012123456Z_a97b42....metadata.json

I have source, dataset, and ingestion data encoded structurally, this makes discovery and partitioning 
much easier down the line.

- I am including the hash in the filename makes the raw artifacts easier to distinguish and the full SHA256
also remains within the metadata too.

- Atomic writes are considered. Writing to temporary file first, only if the writing succeeds do I write the
temporary file to its final name. Therefore, the final path appears only after the complete files exists. 
This is good defense against unreliable / partial writes if the process crashes during ingestion. I dont 
want a file that looks like a complete ingestion artifact when its actually incomplete.

============================================================================================================
"""

@dataclass(frozen=True, slots=True)
class RawArtifact:
    payload_path: Path
    metadata_path: Path
    sha256: str

class RawFileSink:

    def __init__(self, root: Path) -> None:
        self._root: Path = root

    def write(
        self,
        *,
        source: str,
        dataset: str,
        response: HttpResponseSnapshot,
    ) -> RawArtifact:
        payload_hash: str = hashlib.sha256(string=response.body).hexdigest()

        ingestion_date: str = response.received_at.date().isoformat()

        timestamp: str = response.received_at.strftime(format="%Y%m%dT%H%M%S%fZ")

        artifact_name: str = f"{timestamp}_{payload_hash[:16]}"

        target_dir: Path = (
            self._root
            / source
            / dataset
            / f"ingestion_date={ingestion_date}"
        )

        target_dir.mkdir(parents=True, exist_ok=True)

        payload_path: Path = target_dir / f"{artifact_name}.json"
        metadata_path: Path = target_dir / f"{artifact_name}.metadata.json"

        metadata: dict[str, str | int | dict[str, str]] = {
            "source": source,
            "dataset": dataset,
            "receivedAt": response.received_at.isoformat(),
            "requestUrl": response.url,
            "statusCode": response.status_code,
            "headers": response.headers,
            "payloadSha256": payload_hash,
            "payloadBytes": len(response.body),
        }

        self._write_atomic(
            path=payload_path,
            content=response.body,
        )

        self._write_atomic(
            path=metadata_path,
            content=json.dumps(
                obj=metadata,
                indent=2,
                sort_keys=True,
            ).encode(),
        )

        return RawArtifact(
            payload_path=payload_path,
            metadata_path=metadata_path,
            sha256=payload_hash,
        )

    @staticmethod
    def _write_atomic(path: Path, content: bytes) -> None:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = Path(temporary_file.name)

        try:
            os.replace(src=temporary_path, dst=path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise