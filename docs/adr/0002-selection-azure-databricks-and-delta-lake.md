# ADR-0002: Select Azure Databricks and Delta Lake as the Primary Data Platform

---

## Status

Accepted

## Date

2026-09-25

## Context

The initial ADR-0001 established that FluxLine will use a lakehouse oriented, event driven architecture supporting:

* batch ingestion
* streaming ingestion
* Change Data Capture (CDC)
* durable raw data retention
* idempotent replay
* incremental transformation
* governed analytical datasets
* dimensional modelling
* data products
* future machine learning workloads

This ADR is centered around the primary execution and storage platform decision.

Important requirements include:

* Python and SQL development (pyspark / dbt)
* Apache Spark processing
* event time stream processing
* transactional lakehouse storage
* schema enforcement
* incremental transformations
* CDC patterns
* data governance
* lineage
* orchestration
* CI/CD
* infrastructure automation
* observability
* performance optimisation

The platform should also integrate naturally with Azure because FluxLine will use Azure as its primary cloud environment.

---

# Decision

FluxLine will use:

* **Azure Databricks** as its primary data engineering compute platform;
* **Apache Spark / PySpark** as its primary distributed processing engine;
* **Spark Structured Streaming** for distributed streaming transformations;
* **Delta Lake** as its primary lakehouse table format;
* **Azure Data Lake Storage Gen2** as durable cloud object storage;
* **Unity Catalog** for data governance.

Databricks will therefore provide the main execution environment for the Bronze, Silver and Gold data pipelines.

Azure infrastructure surrounding Databricks will remain independently managed where appropriate.

---

# Logical Platform Model

```text
                    Azure

     ┌──────────────────────────────────┐
     │                                  │
     │          ADLS Gen2               │
     │                                  │
     │      Durable Cloud Storage       │
     │                                  │
     └───────────────┬──────────────────┘
                     │
                     ▼
               Delta Lake
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
      Bronze       Silver        Gold
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
            Azure Databricks
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       PySpark      SQL     Structured
                              Streaming
                     │
                     ▼
               Unity Catalog
```

The design intentionally separates:

```text
storage
```

from:

```text
compute
```

Data persists independently of individual Spark clusters or jobs.

---

# Why Databricks Fits FluxLine Well

## 1. Strong Spark Integration

For FluxLine I deliberately wanted to include distributed data processing as a learning and engineering requirement.

Databricks is built around Apache Spark and supports PySpark, SQL and Structured Streaming as core processing technologies.

This directly supports FluxLine workloads including:

* high volume telemetry transformations
* event time processing
* large historical backfills
* distributed joins
* incremental transformations
* performance engineering

It also allows FluxLine to investigate Spark behaviour directly, including:

* partitioning
* shuffles
* broadcast joins
* skew
* adaptive query execution
* caching
* execution plans
* executor behaviour

---

# 2. Delta Lake Matches Replay and Incremental Requirements

FluxLine requires more than storage of Parquet files.

The platform requires:

* ACID table operations
* schema enforcement
* incremental updates
* merge operations
* historical reconstruction
* streaming integration

Databricks uses Delta Lake as the standard lakehouse storage layer. Delta provides transactional table semantics and schema enforcement over cloud object storage.

This makes it suitable for workloads such as:

```text
telemetry
    ↓
deduplication
    ↓
MERGE
    ↓
trusted Silver table
```

and:

```text
CDC events
    ↓
incremental application
    ↓
current state / history
```

Delta Lake will also support later dimensional modelling patterns such as SCD Type 2 and static dimensions where applicable.

---

# 3. Batch and Streaming Share the Same Platform

I have explicitly rejected maintaining completely independent analytical batch and streaming architectures. Instead I want a unified architecture that is more maintainable.

Databricks Structured Streaming integrates directly with Delta Lake.

This means both:

```text
scheduled API ingestion
```

and:

```text
continuous telemetry
```

can ultimately produce governed lakehouse tables.

Conceptually:

```text
API batch
    │
    ├──────────────┐
    │              │
    ▼              ▼
  Bronze        Bronze
                  ▲
                  │
            Event stream
```

The processing mechanisms may differ, but the durable analytical platform does not need to fragment into unrelated systems.

---

# 4. Unity Catalog Provides a Governance Layer

FluxLine requires governance to be implemented rather than merely discussed.

Unity Catalog provides governance capabilities integrated into Databricks, including access controls, lineage and auditing.

I will eventually use this to explore concepts including:

* catalogs
* schemas
* managed tables
* external locations
* privileges
* service identities
* lineage
* auditability

---

# 5. Suitable Production Workflow

Databricks provides platform capabilities for:

* scheduled jobs
* pipeline orchestration
* programmatic resource deployment
* ingestion
* monitoring
* CI/CD oriented development

Current Databricks tooling includes Lakeflow for ingestion and pipeline workloads and Declarative Automation Bundles for programmatically defining and deploying Databricks resources.

This aligns with FluxLine requirements that deployments should be reproducible rather than configured manually through a user interface.

---

# 6. Azure Integration

I has selected Azure as its primary cloud.

Azure Databricks integrates naturally with services that FluxLine is expected to use, including:

* Azure Data Lake Storage Gen2
* Azure Event Hubs
* Azure Key Vault
* Microsoft Entra ID
* Azure Monitor
* managed identities
* Azure networking

This provides a coherent platform while still allowing individual infrastructure components to remain independently managed.

---

# Alternatives Considered

## Alternative 1: Microsoft Fabric

Microsoft Fabric provides a credible modern lakehouse platform.

Its capabilities include:

* Delta Lake based lakehouses
* Spark processing
* Data Factory style pipelines
* OneLake
* Eventstream
* Eventhouse
* Real Time Intelligence
* Power BI integration

Fabric Lakehouse uses Delta Lake as its default table format, while Real Time Intelligence provides dedicated event streaming and event analysis capabilities.

### Advantages

* highly integrated Microsoft analytics ecosystem
* strong Power BI integration
* unified SaaS experience
* capable real time analytics tooling
* reduced infrastructure management

### Disadvantages

I want FluxLine to have a deliberate emphasis on:

* Spark internals
* Structured Streaming
* explicit cloud infrastructure
* deployment architecture
* engineering oriented platform operations

Fabric abstracts some infrastructure concerns that I intentionally want to explore.

Its Real Time Intelligence architecture also introduces concepts such as Eventhouse and KQL that are valuable but would broaden the project's technology surface more than what I want at this time.

### Decision

Not selected as the primary platform.

Fabric remains a credible alternative architecture and may later be investigated comparatively.

---

# Alternative 2: Snowflake

Snowflake provides a mature analytical platform with increasingly broad data engineering functionality.

Relevant capabilities include:

* SQL based transformation
* Snowpark
* Streams
* Dynamic Tables
* Snowpipe
* Snowpipe Streaming
* Apache Iceberg support

Snowflake currently supports streaming ingestion into Snowflake managed Iceberg tables, and Dynamic Iceberg Tables allow incrementally maintained outputs stored in Iceberg format.

### Advantages

* excellent SQL analytics environment
* strong managed service experience
* minimal infrastructure management
* mature analytical ecosystem
* increasingly strong open table format support

### Disadvantages

The project deliberately aims to develop deep expertise in:

* Apache Spark
* PySpark
* Spark execution behaviour
* Structured Streaming
* lakehouse performance engineering

A Snowflake centred architecture would shift the learning emphasis toward Snowflake native processing concepts.

This would not be inherently worse, but it would represent a different project.

### Decision

Not selected.

Snowflake would be appropriate for a differently scoped implementation. Although, it is something I am interested in exploring down the line in other projects.

---

# Alternative 3: Azure Synapse Analytics

Azure Synapse combines:

* SQL analytics
* Apache Spark
* pipelines
* data lake access
* Azure integration

Synapse supports both Spark pools and SQL engines over data stored in Azure Data Lake Storage.

### Advantages

* native Azure integration
* Spark availability
* integrated SQL analytics
* familiar Microsoft ecosystem
* built-in pipeline tooling

### Disadvantages

The lakehouse experience is less unified around the specific combination Fluxline intends to achieve.

For example, some Synapse lake database functionality has limitations around Delta integration and metadata synchronisation between Spark and other interfaces.

Databricks provides a more cohesive environment which closely matches the primary learning goals I have set for myself.

### Decision

Not selected.

---

# Alternative 4: Self Managed Apache Spark

FluxLine could run Apache Spark directly using:

* Kubernetes
* virtual machines
* standalone Spark clusters
* cloud managed container infrastructure

Storage could remain in ADLS using Delta Lake.

### Advantages

* maximum infrastructure control
* deeper understanding of Spark deployment
* reduced vendor dependence
* strong learning opportunity

### Disadvantages

I would then need to operate:

* cluster infrastructure
* Spark deployment
* scaling
* security integration
* job scheduling
* logging
* configuration
* upgrades

A significant portion of the project would become:

> operating Spark infrastructure

rather than:

> engineering reliable data systems.

### Decision

Rejected as the primary architecture.

Local Spark environments may still be used for development and testing where useful.

Although I would like to explore kubernetes further.

---

# Storage Ownership

Azure Data Lake Storage Gen2 will provide durable object storage.

Delta Lake will provide the transactional table abstraction over that storage.

Azure Databricks provides the primary compute and management environment.

Conceptually:

```text
ADLS
│
│  owns durable bytes
│
▼
Delta Lake
│
│  defines transactional tables
│
▼
Databricks
│
│  processes / governs / serves
│
▼
Data Products
```

Understanding this distinction is important.

Databricks is not treated as synonymous with the underlying data itself.

---

# Medallion Architecture

FluxLine will initially use a Bronze, Silver and Gold organisation.

However, these layers describe responsibilities, not arbitrary folders.

## Bronze

Purpose:

> Preserve source information durably.

Characteristics:

* minimally transformed
* replayable
* ingestion metadata attached
* source fidelity prioritised
* invalid source data may still exist

---

## Silver

Purpose:

> Represent trusted canonical domain data.

Typical processing includes:

* schema validation
* data quality checks
* deduplication
* normalisation
* timestamp handling
* reference data enrichment
* valid business entities

---

## Gold

Purpose:

> Represent consumer-oriented data products.

Possible structures include:

* fact tables
* dimensions
* SCD Type 2 dimensions
* aggregates
* operational views
* feature datasets
* domain marts

Gold does not imply one universal modelling technique.

---

# Slowly Changing Dimensions

Where historical analytical context is required, I may implement Slowly Changing Dimension Type 2 models.

For example:

```text
dim_asset
```

could preserve changes to:

```text
rated_capacity
operator
site_assignment
asset_configuration
operational_classification
```

A typical implementation may include:

```text
asset_key
asset_id
valid_from
valid_to
is_current
attribute_hash
```

Change detection may use a deterministic hash over canonicalised tracked attributes.

The specific hashing strategy and temporal merge algorithm will be defined when dimensional modelling is implemented.

---

# Consequences

## Positive

Selecting Azure Databricks provides:

* strong Spark learning opportunities
* integrated Structured Streaming
* native Delta Lake workflows
* unified governance
* Azure integration
* scalable processing
* batch/stream convergence
* production oriented deployment capabilities

It also provides a coherent technical specialisation rather than spreading across multiple overlapping platforms.

---

## Negative

FluxLine becomes partially dependent on Databricks specific platform behaviour.

Examples may include:

* Unity Catalog
* Lakeflow
* Databricks runtime behaviour
* Databricks deployment configuration

Some skills will therefore be platform specific.

The architecture should compensate by distinguishing:

```text
fundamental engineering concept
```

from:

```text
Databricks implementation
```

whenever possible.

For example:

```text
Concept:
Slowly changing dimension

Implementation:
Delta MERGE
```

and:

```text
Concept:
Event-time stream processing

Implementation:
Spark Structured Streaming watermark
```

This distinction is part of my learning philosophy.

---

# Cost Consequence

Databricks is capable of operating infrastructure significantly larger and more expensive than what FluxLine requires during everyday development.

Cloud resources should therefore:

* use appropriately small development compute;
* use serverless or ephemeral compute where justified;
* terminate automatically where possible;
* avoid running continuously without need;
* be provisioned reproducibly;
* distinguish development scale from reference production scale.

Production scale workloads may be simulated temporarily rather than operated continuously to avoid excessive expenditure.

---

# Requirement Traceability

This decision supports:

* FR-01 Batch ingestion
* FR-02 Streaming ingestion
* FR-03 Change Data Capture
* FR-04 Raw-data preservation
* FR-05 Schema validation
* FR-08 Deduplication
* FR-09 Event-time processing
* FR-10 Late-data handling
* FR-11 Backfill
* FR-12 Replay
* FR-13 Incremental transformation
* FR-14 Data-product generation
* FR-15 Lineage
* FR-16 Operational monitoring
* FR-17 Automated deployment

It also directly supports the project's requirements for:

* scalability
* governance
* performance engineering
* reproducibility
* observability
* maintainability

---

# Review Conditions

This decision should be revisited if:

* Databricks cost becomes disproportionate;
* The FluxLine workload no longer justifies distributed Spark processing;
* major platform limitations prevent required functionality;
* the project changes from a Spark-oriented learning objective;
* another platform materially simplifies the architecture without compromising learning objectives.

The selection of Databricks is therefore a reasoned engineering decision, not an assumption that Databricks is universally the best data platform.

---
