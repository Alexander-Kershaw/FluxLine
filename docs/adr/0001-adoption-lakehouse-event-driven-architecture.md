# ADR-0001: Adopt a Lakehouse Oriented, Event Driven Architecture

---

## Status

Accepted

## Date

2026-09-25

## Context

I am designing FluxLine to support several fundamentally different data workloads:

* scheduled ingestion from external APIs
* continuous asset telemetry
* operational database changes
* historical backfills
* event replay
* analytical modelling
* operational reporting
* future forecasting and machine-learning workloads

These workloads differ in:

* latency
* data volume
* mutability
* delivery mechanism
* schema stability
* processing pattern
* retention requirements

The architecture must therefore support both batch and streaming data without creating separate, disconnected platforms.

FluxLine also requires:

* durable raw data retention
* replayability
* idempotent processing
* schema enforcement
* data quality validation
* historical reconstruction
* scalable transformation
* governed analytical datasets
* incremental processing
* observability
* reproducible deployment

The architecture should allow these requirements to coexist without unnecessarily duplicating storage and transformation logic.

---

# Decision

FluxLine will adopt a lakehouse oriented, event driven architecture.

The system will combine:

1. durable object storage;
2. transactional lakehouse tables;
3. batch ingestion;
4. event driven ingestion;
5. stream processing;
6. incremental transformation;
7. governed domain oriented data products.

The logical processing model will broadly follow:

```text
Sources
   │
   ├── APIs
   ├── Operational Databases
   └── Event Streams
          │
          ▼
   Ingestion Layer
          │
          ▼
   Raw / Bronze Layer
          │
          ▼
Validation: Standardization and Normalisation
          │
          ▼
      Silver Layer
          │
          ▼
Business / Domain Modelling
          │
          ▼
       Gold Layer
          │
          ▼
     Data Products
```

Streaming and batch workloads will share the same durable data platform where practical rather than maintaining separate analytical systems, I want to keep everything quite connected within a universal / generic processing pipeline.

---

# Architectural Principles

## 1. Durable raw data is retained

Source data should be preserved sufficiently faithfully to support:

* replay
* debugging
* auditing
* backfills
* transformation correction
* downstream reconstruction

The event broker is therefore not treated as the permanent historical system of record.

---

## 2. Batch and streaming converge on common storage

FluxLine will not maintain entirely separate batch and streaming analytical stores.

Both processing modes should converge into common lakehouse datasets.

Conceptually:

```text
Batch Sources ─────────────┐
                           │
                           ▼
                        Lakehouse
                           ▲
                           │
Streaming Sources ─────────┘
```

This reduces duplicated modelling logic and inconsistent analytical state, reducing points of failure and volume of work.

---

## 3. Event driven ingestion is used where the source behaviour justifies it

Continuous telemetry and database change events are naturally represented as events.

External APIs are not artificially converted into streaming systems where scheduled or incremental batch ingestion is more appropriate.

The architecture therefore supports both:

```text
pull based ingestion
```

and:

```text
event driven ingestion
```

depending on source characteristics.

---

## 4. Processing is incremental where practical

FluxLine should avoid repeatedly recomputing complete datasets when only a small amount of data has changed.

Incremental processing is preferred for:

* telemetry
* CDC
* API updates
* Silver transformations
* Gold data products

Full reconstruction remains possible where required.

---

## 5. Replayability is a priority capability

Processing logic should assume that historical data may need to be processed again.

Examples include:

* correcting transformation bugs
* rebuilding downstream tables
* handling schema changes
* recovering after processing failures
* reproducing historical analytical state

Idempotency and deterministic transformations will therefore influence downstream design.

---

## 6. Gold represents business facing data products

Bronze, Silver and Gold are the implementation layers.

They are not themselves the primary business deliverables.

Gold datasets should represent meaningful products such as:

* Grid State
* Renewable Operations
* Market Intelligence
* Forecast Intelligence
* Sustainability Intelligence

These products may contain:

* dimensional models
* fact tables
* slowly changing dimensions
* aggregates
* current state views
* historical analytical models

The modelling technique should be selected according to the data product's requirements rather than imposing one universal Gold layer design. These will be decided at gold development.

---

# Alternatives Considered

## Alternative 1: Traditional Data Warehouse

A conventional architecture could load operational data directly into a relational analytical warehouse.

### Advantages

* mature SQL tooling
* strong transactional behaviour
* familiar dimensional modelling
* relatively simple BI consumption

### Disadvantages

* less natural for raw high volume telemetry
* expensive or awkward long term raw data retention
* weaker fit for replay heavy event workloads
* streaming may require additional architecture
* scientific and machine learning workloads may require separate storage

### Decision

Rejected as the primary FluxLine architecture.

A warehouse style dimensional model may still appear within Gold where appropriate.

---

## Alternative 2: Data Lake Only

All source data could be stored as files in object storage without a transactional table layer.

### Advantages

* inexpensive storage
* flexible data formats
* easy raw data retention
* highly scalable

### Disadvantages

* weak transactional guarantees
* difficult concurrent updates
* harder incremental processing
* table consistency becomes more complex
* merge and CDC patterns require additional engineering
* schema governance becomes more difficult

### Decision

Rejected.

FluxLine requires stronger table semantics than a file only data lake provides.

---

## Alternative 3: Separate Batch and Streaming Architectures

A Lambda style architecture could maintain:

```text
batch processing path

and 

stream processing path
```

with separate logic later merged into a serving layer.

### Advantages

* independent optimisation of real time and batch workloads
* historically common approach
* clear separation of processing modes

### Disadvantages

* duplicated transformation logic
* increased operational complexity
* risk of inconsistent results between paths
* more systems to deploy, test and maintain

### Decision

Rejected as the default architecture.

FluxLine will instead favour common storage and shared transformation semantics where possible.

---

## Alternative 4: Streaming Only Architecture

All data could be converted into events and processed through a streaming platform.

### Advantages

* unified event model
* low latency processing
* strong replay semantics when carefully designed

### Disadvantages

* scheduled APIs do not naturally require streaming
* historical backfills become unnecessarily complicated
* batch analytics may become harder to reason about
* additional operational complexity without proportional benefit

### Decision

Rejected.

FluxLine uses streaming where event driven behaviour provides genuine value rather than forcing streaming for everything.

---

## Alternative 5: Lakehouse Architecture

A lakehouse combines scalable object storage with transactional table semantics and analytical processing.

### Advantages

* supports batch and streaming
* supports raw and curated data
* facilitates replay
* scalable storage
* transactional table operations
* suitable for analytical and ML workloads
* supports incremental transformation
* appropriate for large telemetry histories

### Disadvantages

* introduces distributed system complexity
* requires careful file and table optimisation
* can encourage poorly governed data dumping if architecture is weak
* operational cost can exceed simpler solutions for small workloads

### Decision

Selected.

Its advantages align directly with FluxLine functional and nonfunctional requirements.

---

# Consequences

## Positive Consequences

FluxLine can support:

* one durable analytical platform
* streaming telemetry
* scheduled API ingestion
* CDC workloads
* historical backfills
* replayable pipelines
* large historical datasets
* incremental transformations
* dimensional Gold models
* slowly changing dimensions
* machine learning consumers

The architecture also creates meaningful opportunities for me to study:

* distributed processing
* storage optimisation
* event time semantics
* CDC
* data modelling
* table versioning
* data governance

---

## Negative Consequences

The architecture introduces complexity that would not be justified for a very small system.

The project must therefore manage:

* distributed computation
* table maintenance
* schema evolution
* checkpointing
* storage layout
* event semantics
* deployment configuration
* cloud cost

Therefore I must resist adding additional distributed components unless requirements justify them.

---

# Relation to Requirements

This decision primarily supports:

* FR-01 Batch ingestion
* FR-02 Streaming ingestion
* FR-03 Change Data Capture
* FR-04 Raw-data preservation
* FR-08 Deduplication
* FR-09 Event-time processing
* FR-10 Late-data handling
* FR-11 Backfill
* FR-12 Replay
* FR-13 Incremental transformation
* FR-14 Data-product generation
* FR-15 Lineage
* FR-16 Operational monitoring

It also supports the nonfunctional requirements concerning:

* reliability
* idempotency
* reproducibility
* scalability
* maintainability
* performance

---

# Implementation Direction

This ADR defines the architectural pattern rather than final vendor selection.

Likely implementation technologies include:

* object storage
* transactional lakehouse tables
* distributed data processing
* an event broker
* an operational relational database
* orchestration
* infrastructure as code
* governance tooling

Individual technology selections will be documented in later ADRs.

---

# Review Conditions

This decision should be revisited if:

* The FluxLine workload becomes too small to justify distributed lakehouse infrastructure;
* latency requirements become incompatible with the chosen processing model;
* operational cost becomes disproportionate;
* a major source requires architecture incompatible with this model;
* evidence from performance testing invalidates core assumptions.

---