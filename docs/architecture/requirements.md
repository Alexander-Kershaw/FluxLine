# FluxLine Architecture Requirements

---

## 1. Purpose

I intend this document to translate the FluxLine project charter into measurable engineering requirements and workload assumptions.

The purpose is not to predict the exact workload of a real energy company, that is too much of a task at this time. Instead, it establishes a plausible reference workload against which architecture, performance, reliability and cost decisions can be sensibly reasoned about.

These assumptions have potential evolve as the platform is developed.

Changes to major assumptions will be documented because they may affect architectural decisions downstream.

---

# 2. Requirement Philosophy

FluxLine distinguishes between three workload profiles:

1. **Development workload**
2. **Reference production workload**
3. **Stress test workload**

This allows the platform to model production scale engineering problems without requiring full production scale infrastructure during everyday development as this would be cumbersome and expensive for just a portfolio project.

The architecture should therefore be capable of scaling beyond the normal local development workload.

---

# 3. Workload Profiles

## 3.1 Development Profile

The development profile is intended for local development and inexpensive cloud testing.

Assumptions:

| Property                       |                  Development Value |
| ------------------------------ | ---------------------------------: |
| Simulated assets               |                                 25 |
| Telemetry interval             |                         10 seconds |
| Average telemetry rate         |                  2.5 events/second |
| Events per day                 |                            216,000 |
| External API sources           |                                2–4 |
| PostgreSQL operational records |                           <100,000 |
| Primary purpose                | Functional development and testing |

This workload should be small enough to run comfortably without requiring super advanced hardware, while also keeping costs relatively low.

---

## 3.2 Reference Production Profile

The reference production profile represents the fictional Asteria Energy production environment.

Assumptions:

| Property                            |  Reference Value |
| ----------------------------------- | ---------------: |
| Active assets                       |              300 |
| Telemetry interval                  |       10 seconds |
| Average telemetry rate              | 30 events/second |
| Telemetry events per minute         |            1,800 |
| Telemetry events per hour           |          108,000 |
| Telemetry events per day            |        2,592,000 |
| Telemetry events per year           |     ~946 million |
| External API sources                |             5–10 |
| Operational DB records              |     1–10 million |
| Concurrent downstream data products |               5+ |

I intend the developed architecture to comfortably accommodate this workload without requiring redesign.

---

## 3.3 Stress Test Profile

The stress test profile intentionally exceeds the expected reference workload.

Assumptions:

| Property               |      Stress Value |
| ---------------------- | ----------------: |
| Active assets          |             3,000 |
| Telemetry interval     |        10 seconds |
| Average telemetry rate | 300 events/second |
| Events per day         |        25,920,000 |

This profile exists to expose bottlenecks and demonstrate scaling behaviour.

It is not expected to run continuously.

---

# 4. Telemetry Volume Derivation

The reference workload assumes:

```text
300 assets
×
1 event every 10 seconds
```

Each asset therefore produces:

```text
6 events/minute
```

Across 300 assets:

```text
300 × 6
=
1,800 events/minute
```

Therefore:

```text
1,800 × 60
=
108,000 events/hour
```

And:

```text
108,000 × 24
=
2,592,000 events/day
```

Approximately:

```text
2.592 million events/day
```

Over one year:

```text
2,592,000 × 365
≈
946 million events
```

This is large enough to make distributed processing, partitioning, incremental processing and data layout meaningful engineering concerns.

---

# 5. Event Size Assumption

A typical telemetry event is expected to contain fields such as:

```text
event_id
asset_id
site_id
event_timestamp
ingestion_timestamp
power_mw
available_capacity_mw
temperature_c
status
quality_code
```

For initial capacity planning, assuming approximately:

```text
1 KB/event
```

before compression and columnar storage optimisation.

At the reference workload:

```text
2,592,000 events/day
×
1 KB
≈
2.6 GB/day
```

This produces approximately:

```text
~78 GB / 30 days

~237 GB / 90 days

~946 GB / year
```

of logical uncompressed telemetry.

Actual Delta/Parquet storage should generally be lower because of columnar compression (columnstore indexing), although additional metadata, versions and derived datasets also consume storage. Although this is not of massive concern since modern data engineering largely favours ELT since cloud storage is generally inexpensive. 

These calculations therefore represent planning estimates rather than precise storage forecasts.

---

# 6. Data Source Characteristics

FluxLine is intended to support several fundamentally different source types.

## 6.1 Public APIs

Examples include:

* electricity system data
* carbon intensity data
* weather data

Characteristics may include:

* HTTP request/response interaction
* rate limits
* temporary failures
* pagination
* source side revisions
* variable update frequencies
* historical endpoints
* schema evolution

API ingestion must not assume that every request succeeds.

---

## 6.2 Asset Telemetry

Telemetry represents continuous event data generated by physical assets.

Characteristics include:

* high frequency
* event timestamps
* duplicate delivery
* late arrival
* out of order arrival
* bursts
* missing intervals
* malformed records

Telemetry processing must distinguish:

```text
event time
```

from:

```text
processing time
```

processing time is useful ingestion / transformation metadata, and is distinct from the actual event entity timestamp originating from a data source.

---

## 6.3 Operational Database

PostgreSQL represents transactional business systems (OLTP).

Characteristics include:

* inserts
* updates
* deletes
* mutable current state
* relational constraints
* relatively low event frequency compared with telemetry

Changes are eventually be captured incrementally using Change Data Capture rather than repeated full table extraction. This is more computationally efficient, re-reading entire tables should not happen especially with accumulations of batch and streamed data into the lakehouse.

---

# 7. Latency Requirements

Different data products have different latency requirements.

Therefore I have not designated one universal latency target.

## 7.1 Telemetry Bronze Ingestion

Target:

```text
95% of valid telemetry events persisted to Bronze
within 30 seconds of ingestion by FluxLine.
```

This measures platform processing latency rather than network delay between a physical asset and the platform.

---

## 7.2 Telemetry Silver Availability

Target:

```text
95% of valid telemetry events available in trusted Silver datasets
within 2 minutes of platform ingestion.
```

Silver processing includes standardization and DQ enforcement activities such as:

* schema validation
* normalisation
* deduplication
* data quality checks
* enrichment

---

## 7.3 Operational Gold Products

Target:

```text
Operational Gold datasets should reflect accepted Silver telemetry
within 5 minutes.
```

Examples include:

* current asset generation
* fleet availability
* recent generation totals

---

## 7.4 External API Data

External source freshness depends on the source's own publication frequency.

The initial objective is:

```text
New source data should normally become available in Silver
within 15 minutes of becoming available upstream.
```

This requirement may later be specialised by source.

---

## 7.5 Analytical Products

Historical analytical products do not require second level latency.

Target:

```text
Scheduled analytical products should complete within their
documented batch window.
```

Exact batch windows will be defined when those products are introduced.

---

# 8. Availability and Recovery Objectives

FluxLine is not intended to model life critical grid control infrastructure.

Its reliability objectives therefore represent an internal analytics and operations data platform rather than a real time control system.

## Platform Availability Objective

Target:

```text
99.5% monthly availability
```

for production ingestion and processing services.

This allows approximately:

```text
3 hours 39 minutes
```

of unavailable time in a 30 day month.

This is an engineering target rather than a contractual SLA (Service Level Agreement).

---

## Recovery Time Objective

For significant pipeline failure:

```text
RTO: 60 minutes
```

Meaning:

> The platform should normally be capable of restoring critical ingestion and processing functionality within one hour.

---

## Recovery Point Objective

For data that has already reached a durable source or broker:

```text
RPO: effectively zero logical data loss
```

This does not mean every downstream table must update instantly.

It means recoverable source data should remain available for replay rather than being permanently lost because a processing job failed.

---

# 9. Replay Requirements

Replayability is a fundamental FluxLine requirement.

The platform should support rebuilding downstream datasets from retained upstream data.

Examples include:

```text
Bronze
-> rebuild Silver
-> rebuild Gold
```

and:

```text
event broker
-> replay consumer
-> rebuild Bronze
```

Replay must not create uncontrolled duplication.

Where possible, transformations should therefore be deterministic and idempotent.

---

# 10. Backfill Requirements

External API ingestion must support historical backfills.

Initial requirement:

```text
At least 365 days of historical source data should be backfillable
when the upstream source provides that history.
```

Backfills should use the same validation rules as routine ingestion.

Backfill execution should not require manually modifying production application code.

Date ranges or equivalent boundaries should instead be supplied through explicit configuration or runtime parameters.

---

# 11. Late Arriving Telemetry

Telemetry may arrive after its event timestamp.

Therefore I must not assume:

```text
arrival order == event order
```

For the reference workload, the system should handle routine telemetry lateness of:

```text
up to 10 minutes
```

without treating otherwise valid data as unusable.

Events arriving later than the standard lateness threshold should remain observable and must not silently disappear.

The exact watermarking strategy ultimately will be decided when streaming processing is designed.

---

# 12. Duplicate Data

Duplicate records are expected as with any data oridented system.

Possible causes include:

* producer retries
* broker redelivery
* API retry behaviour
* replay
* pipeline restart
* accidental source duplication

Telemetry events will therefore require stable identifiers such as:

```text
event_id
```

Where source data provides natural identifiers, those identifiers should be preferred.

Where it does not, I may derive deterministic keys from stable source attributes.

---

# 13. Missing Data

Absence of records does not always mean absence of activity.

For example:

```text
no turbine telemetry
```

could mean:

1. the turbine generated zero power;
2. the turbine was offline;
3. connectivity was lost;
4. the producer failed;
5. the ingestion pipeline failed.

FluxLine must avoid silently interpreting missing telemetry as a valid zero measurement.

Freshness and missing event detection should therefore become part of data quality monitoring.

---

# 14. Schema Evolution

Source schemas are expected to evolve.

Potential changes include:

* new optional fields
* removed fields
* renamed fields
* changed data types
* changed semantics

FluxLine must detect schema changes.

Breaking changes must not silently propagate into trusted datasets.

The platform should distinguish between:

```text
compatible schema evolution
```

and:

```text
breaking schema evolution
```

Detailed compatibility rules will be defined when data contracts are implemented.

---

# 15. Data Retention

Initial logical retention objectives are:

## Bronze / Raw

```text
Minimum: 1 year
```

for datasets where licensing and source constraints allow it.

Bronze data exists primarily to support:

* replay
* debugging
* auditing
* historical reconstruction

---

## Silver

```text
Minimum: 1 year
```

for operational analytical datasets.

Longer retention may be used where historically valuable.

---

## Gold

Retention depends on the individual data product.

Aggregated historical datasets may be retained indefinitely within the scope of the project.

---

## Event Broker

Initial target:

```text
7 days
```

of event retention.

The event broker is not intended to be the permanent historical system of record.

Bronze storage fulfills that responsibility.

---

# 16. Data Quality Requirements

FluxLine must support validation across several dimensions.

## Schema Quality

Examples:

* required fields exist
* types are valid
* structures match the expected contract

## Completeness

Examples:

* required identifiers are populated
* expected telemetry has arrived

## Validity

Examples:

```text
state_of_charge between 0 and 100
```

## Uniqueness

Examples:

```text
event_id should uniquely identify a telemetry event
```

## Referential Integrity

Examples:

```text
telemetry.asset_id
must reference a known asset, it should not be orphaned
```

## Freshness

Examples:

```text
latest turbine measurement
must not be older than an accepted threshold
```

Quality failures must produce observable results.

Invalid records must not simply vanish.

---

# 17. Quarantine Requirements

Records that cannot safely enter trusted datasets should be quarantined.

Quarantined records should preserve enough information to investigate:

* original payload
* source
* ingestion timestamp
* violated rule
* error details
* pipeline run identifier

Where practical, corrected records should be capable of re-entering normal processing.

---

# 18. Observability Requirements

FluxLine must expose both:

## System Observability

Examples:

```text
pipeline success
pipeline failure
execution duration
API latency
broker lag
records processed
retry count
```

and:

## Data Observability

Examples:

```text
freshness
record volume
null-rate changes
schema violations
duplicate rate
quarantine rate
missing telemetry
```

A successful pipeline execution must not automatically imply healthy data.

---

# 19. Initial Operational Metrics

Candidate metrics include:

```text
fluxline_records_ingested_total

fluxline_records_quarantined_total

fluxline_pipeline_duration_seconds

fluxline_pipeline_failures_total

fluxline_source_request_failures_total

fluxline_source_latency_seconds

fluxline_data_freshness_seconds

fluxline_duplicate_events_total

fluxline_late_events_total

fluxline_schema_violations_total

fluxline_consumer_lag
```

Exact implementation will be determined when the observability architecture is designed.

---

# 20. Security Requirements

The production style environment must follow these principles:

* no credentials committed to Git
* secrets stored in an appropriate secret management system (like databricks secrets scope)
* service identities used instead of personal credentials where practical
* least privilege access
* separation between development and production style environments
* auditable access to governed datasets

Sensitive configuration must not be embedded directly in application source code.

---

# 21. Reproducibility Requirements

A new developer should eventually be able to recreate the environment using version controlled configuration.

This includes:

```text
Python environment
infrastructure
containers
pipeline configuration
data contracts
database schemas
Databricks resources
deployment configuration
```

---

# 22. Testing Requirements

The final platform should contain multiple levels of testing.

## Unit Tests

Test individual application components without requiring cloud infrastructure.

## Property Based Tests

Test behavioural invariants across generated inputs.

## Contract Tests

Verify assumptions about schemas and external interfaces.

## Integration Tests

Verify interaction between real infrastructure components such as:

```text
Python
PostgreSQL
Kafka
```

## Pipeline Tests

Validate data transformations using known inputs and expected outputs.

## End to End Tests

Validate complete flows through multiple platform layers.

## Recovery Tests

Intentionally cause failures and verify correct recovery.

## Performance Tests

Measure throughput and latency against defined workload profiles.

---

# 23. Performance Requirements

At the reference workload, the streaming architecture must sustain:

```text
30 events/second average
```

without accumulating persistent processing lag.

Testing should additionally demonstrate behaviour at:

```text
300 events/second
```

or greater during controlled stress tests.

Performance must be measured rather than inferred.

Candidate measurements include:

* events processed per second
* end to end latency
* Spark shuffle volume
* broker lag
* batch duration
* files scanned
* bytes processed
* executor utilisation

---

# 24. Cost Awareness

I am having FluxLina as a portfolio and learning platform rather than a continuously funded enterprise environment.

Architecture must therefore distinguish between:

```text
logical production requirements
```

and:

```text
resources actually operated continuously
```

Large scale workloads may be simulated temporarily.

Development infrastructure should be capable of being shut down when not required.

Infrastructure as Code (IAC) should make environments reproducible rather than encouraging permanently running resources to mitigate prolonged expenses.

---

# 25. Scaling Principle

The application should avoid hardcoding assumptions that prevent scaling between workload profiles.

For example, the following should eventually be configurable:

```text
asset count
telemetry frequency
batch size
partition count
date ranges
source endpoints
retry policies
lateness thresholds
```

Configuration does not mean every possible value must work.

It means workload assumptions should be explicit rather than buried invisibly inside application logic.

---

# 26. Requirement Traceability

Major architectural decisions should reference the requirement they satisfy.

For example:

```text
Requirement:
Replay telemetry after consumer failure.

Potential architectural response:
Durable broker retention and immutable Bronze storage.
```

Architecture Decision Records should identify relevant requirements wherever practical.

This prevents technologies from being introduced without a documented purpose.

---

# 27. Current Reference Targets

The initial FLUXLINE engineering targets can therefore be summarised as:

| Requirement                         |                                 Target |
| ----------------------------------- | -------------------------------------: |
| Reference assets                    |                                    300 |
| Telemetry rate                      |                          30 events/sec |
| Telemetry volume                    |                      2.592M events/day |
| Stress workload                     |                         300 events/sec |
| Bronze telemetry latency p95        |                            <30 seconds |
| Silver telemetry latency p95        |                             <2 minutes |
| Operational Gold latency            |                             <5 minutes |
| External API availability in Silver | <15 minutes after upstream publication |
| Routine late event tolerance        |                             10 minutes |
| API historical backfill             |              ≥365 days where supported |
| Event broker retention              |                                 7 days |
| Raw data retention                  |                                ≥1 year |
| Recovery Time Objective             |                             60 minutes |
| Recoverable data RPO                |          effectively zero logical loss |
| Availability objective              |                                  99.5% |
| Production reference events/year    |                           ~946 million |

These values are the current working engineering assumptions.

They may be modified when implementation evidence demonstrates that different targets would be more appropriate.

Any substantial change will be documented rather than silently altered.

---
