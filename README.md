# DaxwellOps Analytics

**Production-Style KPI Pipeline with Data Quality Enforcement**
*Airflow • dbt • PostgreSQL • Metabase*

A solo, end-to-end analytics engineering project that simulates a manufacturing and wholesale reporting environment similar to Daxwell.

This project demonstrates how operational data can be ingested, modeled into governed KPI tables, validated through automated tests, and delivered through a stakeholder-ready dashboard — with reliability enforced by an Airflow quality gate.

**Repository:** [https://github.com/Minalspawar/daxwellops-analytics](https://github.com/Minalspawar/daxwellops-analytics)

**Demo (5–10 min walkthrough):** [https://youtu.be/82sCjMfEk0g](https://youtu.be/82sCjMfEk0g)

---

## Executive Intent

In operational environments, dashboards often fail not because of visualization issues, but because of inconsistent logic and weak data validation.

This project was built to demonstrate three core capabilities:

1. Standardizing KPI definitions using a governed transformation layer
2. Enforcing data quality before metrics reach stakeholders
3. Operationalizing the pipeline with orchestration, retries, and structured logs

Rather than focusing only on dashboard outputs, this system emphasizes reliability, traceability, and architectural discipline.

---

## Business Questions Addressed

Operations and Finance teams require consistent answers to critical service and compliance questions:

- Are we shipping orders On Time and In Full (OTIF)?
- What percentage of demand are we fulfilling (Fill Rate)?
- How frequently are we creating backorders?
- Are we losing revenue due to contract price mismatches or MOQ violations?

This project translates raw operational data into governed KPI marts that answer those questions with validated logic.

---
## Dashboard Layer — Stakeholder Interface

The Metabase dashboard, titled “DaxwellOps KPI Command Center,” represents the executive consumption layer of the architecture.

It reads directly from validated tables in the analytics schema and provides interactive monitoring of service performance and compliance risk.

## Core KPI Cards

1. OTIF Rate (Overall)
- Measures the percentage of orders shipped on time and in full.
- Business implication: Evaluates service reliability and customer satisfaction.

2. Fill Rate (Overall)
- Calculates total quantity shipped divided by total quantity ordered.
- Business implication: Assesses supply adequacy and demand fulfillment efficiency.

3. Backorder Rate (Overall)
- Shows the percentage of orders that were not completely fulfilled.
- Business implication: Highlights operational bottlenecks or inventory gaps.

4. Contract Leakage ($ Impact)
- Aggregates estimated financial impact from price mismatches and MOQ violations.
- Business implication: Quantifies compliance risk and revenue exposure.

# Trend Analysis

### Weekly OTIF Trend
Visualizes performance over time, enabling detection of service degradation or improvement.

This supports weekly operations reviews and monthly performance reporting.

### Interactivity & Filtering

The dashboard includes a global date filter, allowing stakeholders to dynamically adjust reporting periods. All KPI cards and trend charts update automatically based on the selected timeframe.
This mirrors how real operational dashboards are used in executive review meetings.

<img width="925" height="371" alt="mb_02_dashboard_full" src="https://github.com/user-attachments/assets/04fb0b1f-8854-49c0-848f-e09648797606" />



---
## Architecture Overview

### End-to-End Flow

Landing Files → PostgreSQL (Raw Schema) → dbt Models → Airflow Quality Gate → Metabase Dashboard

<img width="572" height="356" alt="doc_01_architecture" src="https://github.com/user-attachments/assets/8d1b3bec-40ec-4abb-a2e7-d3941132d749" />


### Layer Responsibilities

**Landing Layer**
Synthetic CSV and JSON files are generated to simulate manufacturing operations.

**PostgreSQL (Warehouse)**
Stores raw ingestion tables and analytics-ready marts in separate schemas.

**dbt (Transformation + Governance)**
Implements staging models and final KPI fact tables.
Defines business logic in version-controlled SQL.
Runs automated tests to validate structural and business constraints.

**Airflow (Orchestration + Quality Gate)**
Controls execution order.
Runs `dbt run` followed by `dbt test`.
Blocks downstream consumption if validation fails.
Provides retry capability and structured JSON logs for observability.

**Metabase (Stakeholder Interface)**
Consumes only validated fact tables to present executive KPI dashboards.

---

## Analytical Outputs

### analytics.fact_fulfillment

Provides standardized service performance metrics including:

- OTIF flag

- Shipped vs ordered quantities

- Backorder indicators

- Lead-time calculations

Supports service-level monitoring and supply performance analysis.

---

### analytics.fact_contract_violations

Identifies compliance risks including:
- Contract price mismatches
- Minimum Order Quantity violations
- Estimated revenue impact

Supports financial oversight and contract governance.

---

## Reliability & Data Governance

The Airflow DAG `daxwellops_dbt_quality_gate` enforces validation as a required step.

- Execution sequence:

1. dbt run → builds staging and fact models
2. dbt test → validates integrity and business rules

If tests fail, the pipeline halts and KPIs are not exposed.

- Structured JSON logs capture:

* Command start
* Command result
* Runtime duration

A failure injection and recovery scenario is included to demonstrate real-world robustness.

This design simulates production-grade governance where reliability is prioritized over speed.

---

## Technology Stack

- Docker Desktop — reproducible containerized environment
- PostgreSQL — analytical warehouse with raw and analytics schemas
- dbt-postgres — transformation modeling and automated testing
- Apache Airflow — orchestration, retries, observability, quality gate
- Python + Pandas — synthetic data generation and ingestion
- Metabase — stakeholder dashboards

---

## Dataset Simulation

The synthetic dataset mirrors a manufacturing/wholesale workflow and includes:

- sales_orders.csv — order placement and promised shipment data
- shipments.json — semi-structured shipment events
- contracts.csv — contract pricing and MOQ constraints
- inventory_snapshots.csv — inventory position
- production_batches.csv — production output

Landing directory: `data/landing/`

Warehouse schema: `raw.*` → transformed into `analytics.*`

The dataset intentionally includes cross-domain dependencies to simulate realistic KPI derivation and compliance analysis.

---

## Performance Considerations

Two optimization patterns are demonstrated:
1. Precomputed KPI marts

Metabase reads from analytics.fact_* tables to avoid repeated multi-table joins.

2. Indexes on filter and join columns
   
Indexes are added for commonly queried fields such as order_date, customer_id, and issue_type.

#### Sample EXPLAIN ANALYZE results:

Weekly OTIF: ~2.936 ms

Filtered OTIF (last 60 days): ~2.297 ms

See performance screenshots in the docs folder.

---

## Failure Injection & Recovery Demonstration

The project includes a controlled negative-quantity insertion scenario to show:

1. dbt test failure
2. Airflow task failure state
3. Correction of invalid record
4. Successful re-run

This demonstrates operational resilience and proper governance enforcement.

---

## How to Run

- Start services:

docker compose up -d
docker ps

- Access:

Airflow: [http://localhost:8080](http://localhost:8080)
Metabase: [http://localhost:3000](http://localhost:3000)

- Generate landing data:

python scripts/generate_synthetic_data.py

- Initialize schemas and load raw data via provided scripts.

- Run dbt models and tests from inside the container or trigger via Airflow.

#### Example KPI Query (Source-of-Truth)

1. To compute OTIF, Fill Rate, and Backorder Rate directly from the database:

select
  round(avg((otif)::int) * 100, 2) as otif_rate_pct,
  round((sum(qty_shipped_total)::numeric / nullif(sum(qty_ordered), 0)) * 100, 2) as fill_rate_pct,
  round(avg((not in_full)::int) * 100, 2) as backorder_rate_pct
from analytics.fact_fulfillment;


2. To view contract leakage:

select issue_type,
       count(*) as rows,
       round(sum(est_revenue_impact)::numeric, 2) as total_impact
from analytics.fact_contract_violations
group by 1
order by total_impact desc;


---

## Limitations

- Synthetic dataset (simulated domain)
- Batch processing only
- Local Docker deployment (architecture portable to cloud environments)

---

## Potential Extensions

- Incremental model builds and partitioningAutomated alerts on pipeline failure
- Data lineage documentation via dbt docs
- Cloud deployment (EKS / EMR / managed Postgres)
- Streaming ingestion for shipment events

---

## What This Project Demonstrates

- End-to-end analytics architecture design
- KPI standardization and governance
- Data quality enforcement through automated tests
- Orchestrated execution with observable logs
- Production-style reproducibility via containerization
- Translation of operational data into executive-level insights

---

