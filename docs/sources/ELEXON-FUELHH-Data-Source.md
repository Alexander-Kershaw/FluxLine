# Elexon FUELHH Source Profile

---

## 1. Source Summary

**Provider:** Elexon
**Platform:** Insights Solution / BMRS
**Dataset:** FUELHH
**Description:** Half hourly generation outturn by fuel type
**Geographic scope:** Great Britain electricity system
**Access method:** Public REST API
**Authentication:** None required
**Primary FLUXLINE domain:** Grid
**Initial FLUXLINE consumer:** Grid State data product

---

# 2. Why FluxLine Uses This Dataset

FUELHH is the first production data source integrated into FluxLine.

It was selected because it provides a useful but relatively understandable dataset with which to develop the first ingestion architecture.

It introduces several important data engineering concepts without requiring an excessively complex initial domain model:

* HTTP API ingestion
* date bounded extraction
* historical backfills
* settlement period data
* source schema validation
* deterministic record identity
* duplicate handling
* raw data preservation
* idempotent ingestion
* incremental loading

It will later contribute to core analytical metrics such as:

* generation by fuel type
* renewable generation share
* low carbon generation share
* thermal generation share
* generation mix trends

---

# 3. Business Meaning

FUELHH represents electricity generation aggregated into fuel type categories.

Values represent average generation in megawatts during a settlement period.

Conceptually:

```text
Settlement Period
       │
       ├── CCGT
       ├── Nuclear
       ├── Wind
       ├── Biomass
       ├── Hydro
       ├── Interconnectors
       └── Other
```

The dataset therefore describes the generation mix of the Great Britain electricity system over time.

---

# 4. Expected Grain

The expected source grain is approximately:

One record per:

settlement date
× settlement period
× fuel type
× potentially publication/revision

The exact identity semantics remain under investigation.

with generation categories represented as attributes of that observation.

Conceptually:

```text
Settlement Date   Settlement Period   Fuel Type   Generation
2026-09-20        48                  BIOMASS     2960
2026-09-20        48                  CCGT        5524
2026-09-20        48                  COAL        0
2026-09-20        48                  INTEW      -346
...
```

The exact live API schema will be inspected before a formal data contract is created.

FluxLine must not rely solely on historical documentation when defining the production contract.

---

# 5. Source Endpoint

The current Elexon Insights API uses the following API family:

```text
https://data.elexon.co.uk/bmrs/api/v1/
```

The FUELHH dataset endpoint is:

```text
datasets/FUELHH
```

A typical request can restrict data using settlement date boundaries.

FluxLine will request JSON during application ingestion.

The exact accepted parameters and returned metadata will be verified against live API responses before any client implementation.

---

# 6. Authentication

The Insights Solution APIs are publicly accessible and currently require no API key.

FluxLine therefore does not introduce unnecessary credentials or secret management configuration for this source.

This is source specific.

Other future sources will likely require some authentication.

---

# 7. Frequency

FUELHH is half hourly data.

The source therefore produces a relatively low volume dataset compared with future asset telemetry.

This makes it suitable for the first ingestion implementation because correctness can be developed before introducing high throughput streaming concerns.

---

# 8. Time Semantics

The dataset uses electricity settlement dates and settlement periods.

Therefore, FluxLine does not assume that:

```text
settlement period
```

is equivalent to a simple fixed UTC timestamp without further interpretation.

Great Britain uses daylight saving time transitions.

Settlement days can therefore behave differently around clock changes.

Time conversion will be treated as explicit domain logic rather than inferred casually.

The source values should initially be preserved faithfully in the Bronze layer of the data lakehouse.

Derived canonical timestamps may be introduced in Silver.

---

# 9. Initial Record Identity

The expected natural identity of a FUELHH observation is likely based on:

```text
settlement_date
+
settlement_period
```

Potential complications include:

* revisions
* active/inactive versions
* republished records
* source corrections

Therefore this combination must not be declared a permanent primary key until live source behaviour has been inspected.

FluxLine will investigate source revision semantics before defining deduplication behaviour.

---

# 10. Raw/Bronze Ingestion Philosophy

The first ingestion layer will preserve the source response as faithfully as practical.

Bronze ingestion will avoid prematurely:

* renaming business fields
* deriving analytical measures
* converting the dataset into dimensional form
* removing unfamiliar attributes
* discarding source metadata

The purpose of Bronze is preservation and replay.

Normalisation belongs later in Silver.

---

# 11. Incremental Ingestion

Routine ingestion will request bounded periods rather than repeatedly downloading all historical data.

Conceptually:

```text
previous successful boundary
        ->
new source data
        ->
Bronze
```

However, the implementation must support explicit historical ranges for backfills.

Example:

```text
2026-01-01
    ->
2026-03-31
```

The same ingestion component should ultimately support both routine loads and backfills.

---

# 12. Idempotency Requirement

Running the same logical ingestion more than once must not corrupt downstream data.

For example:

```text
request 2026-09-20
        ->
write data

request 2026-09-20 again
        ->
must not accidentally create incorrect duplicated state
```

The exact mechanism will be decided when Bronze storage is implemented.

Raw response preservation and trusted table deduplication may use different strategies.

---

# 13. Expected Failure Modes

The client must eventually account for conditions including:

```text
connection failure
timeout
HTTP 4xx response
HTTP 5xx response
malformed response
empty response
unexpected schema
partial historical availability
source side revision
```

Retries must be used selectively.

For example, retrying a temporary server failure may be sensible.

Repeatedly retrying an invalid request is generally not.

---

# 14. Schema Strategy

The initial development process will distinguish between three schemas:

```text
source schema
    ->
Bronze representation
    ->
canonical Silver schema
```

These are deliberately not assumed to be identical.

The source schema describes what Elexon itself publishes.

Bronze records what FluxLine received.

Silver describes how FluxLine wants to represent the domain consistently.

---

# 15. Fields to Investigate

Live source inspection should determine the semantics and types of fields relating to:

```text
settlement date
settlement period
fuel categories
interconnectors
active/revision indicators
publication metadata
```

No formal Pydantic or Spark schema should be written until this inspection is complete and I am completely satisfied with the meaning of the data fields.

---

# 16. Data Quality Questions

Before declaring FUELHH trusted, I will investigate questions such as:

```text
Are settlement periods duplicated?

Are records revised?

Can generation values be null?

Can generation values be negative?

Can fuel categories disappear?

Can new fuel categories appear?

How are interconnector exports represented?

How are DST transition days represented?

What does the active flag mean in practice?
```

These questions will inform the later data contracts in Silver.

---

# 17. Known Architectural Use

The expected long term flow is:

```text
Elexon FUELHH
      ->
API ingestion
      ->
Bronze
      ->
schema and quality validation
      ->
Silver generation outturn
      ->
Gold Grid State
```

Potential later consumers include:

```text
generation mix
renewable share
carbon analysis
forecast reconciliation
historical trend analysis
```

---

# 18. Validation Before Implementation

Before building an API client, I will manually inspect a live FUELHH response.

This inspection will establish:

* HTTP behaviour
* request parameters
* response envelope
* field names
* field types
* null behaviour
* source metadata
* record counts
* revision related fields

The inspected response will then inform the first explicit source model and test fixtures.

---

# 19. Current Status

**Source selected.**

Formal schema:

**Not yet accepted.**

Ingestion implementation:

**Not yet started.**

Next action:

> Perform a live API probe and inspect the response before writing application abstractions.

---

# 20. Probe Observation

**Observed on 2026-09-20:**

Records: 960
Settlement periods: 48
Fuel types: 20
Rows per settlement period: 20
Null values: 0
Candidate key duplicates: 0
Records with negative generation: 321

**Observed fuel types:**
```
Fuel types (20):
['BIOMASS', 'CCGT', 'COAL', 'INTELEC', 'INTEW', 'INTFR', 'INTGRNL', 'INTIFA2', 'INTIRL', 'INTNED', 'INTNEM', 'INTNSL', 'INTVKL', 'NPSHYD', 'NUCLEAR', 'OCGT', 'OIL', 'OTHER', 'PS', 'WIND']
```

**Observed grain:**
settlementDate × settlementPeriod × fuelType

Historical identity remains under investigation because Elexon
supports publication time retrieval and superseded dataset records.

---
