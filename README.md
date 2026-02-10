# daxwellops-analytics
## Performance Optimization for Analytical Queries

To support fast, repeatable BI queries, this project applies optimization at two levels:

1) **Model-level optimization (dbt marts)**
- Dashboard queries are served from **materialized marts** (`analytics.fact_*`) instead of raw multi-table joins.
- This reduces query complexity and improves dashboard responsiveness.

2) **Database-level optimization (indexes)**
- Added indexes on commonly filtered and joined columns to prepare the warehouse for scale:
  - `analytics.fact_fulfillment(order_date, customer_id, sku_id)`
  - `analytics.fact_contract_violations(issue_type, order_date)`
  - Supporting raw-layer indexes where appropriate (`raw.sales_orders(order_date)`, `raw.shipments(order_id)`)

3) **Proof using EXPLAIN ANALYZE**
- Verified execution plans and runtime using Postgres `EXPLAIN (ANALYZE, BUFFERS)` on a dashboard-like query (weekly OTIF trend).
- Observed execution times:
  - Weekly OTIF (full scan): **2.936 ms**
  - Weekly OTIF (filtered last 60 days): **2.297 ms**
- Because the demo dataset is small, Postgres chooses **Seq Scan**. In production-sized datasets, indexes become more beneficial for date filtering and joins.

**Screenshots**
- ![EXPLAIN weekly OTIF](docs/perf_01_explain_analyze_otif_weekly.png)
- ![EXPLAIN OTIF filtered](docs/perf_02_explain_analyze_otif_filtered.png)


## Performance Optimization for Analytical Queries

To support fast, repeatable BI queries, this project applies optimization at two levels:

1) **Model-level optimization (dbt marts)**
- Dashboard queries are served from **materialized marts** (`analytics.fact_*`) instead of raw multi-table joins.
- This reduces query complexity and improves dashboard responsiveness.

2) **Database-level optimization (indexes)**
- Added indexes on commonly filtered and joined columns to prepare the warehouse for scale:
  - `analytics.fact_fulfillment(order_date, customer_id, sku_id)`
  - `analytics.fact_contract_violations(issue_type, order_date)`
  - Supporting raw-layer indexes where appropriate (`raw.sales_orders(order_date)`, `raw.shipments(order_id)`)

3) **Proof using EXPLAIN ANALYZE**
- Verified execution plans and runtime using Postgres `EXPLAIN (ANALYZE, BUFFERS)` on a dashboard-like query (weekly OTIF trend).
- Observed execution times:
  - Weekly OTIF (full scan): **2.936 ms**
  - Weekly OTIF (filtered last 60 days): **2.297 ms**
- Because the demo dataset is small, Postgres chooses **Seq Scan**. In production-sized datasets, indexes become more beneficial for date filtering and joins.

**Screenshots**
- ![EXPLAIN weekly OTIF](docs/perf_01_explain_analyze_otif_weekly.png)
- ![EXPLAIN OTIF filtered](docs/perf_02_explain_analyze_otif_filtered.png)


---

## Project Visuals (Architecture + Proof)

### Architecture
![Architecture](docs/doc_01_architecture.png)

### KPI Dashboard (Metabase)
![KPI Dashboard](docs/mb_02_dashboard_full.png)

### Airflow Quality Gate (dbt_run ? dbt_test)
![Airflow DAG](docs/airflow_01_dag_graph.png)

### Structured JSON Logs (Reliability / Observability)
![Structured Logs](docs/airflow_02_structured_logs.png)

### Performance Proof (EXPLAIN ANALYZE)
![EXPLAIN Weekly OTIF](docs/perf_01_explain_analyze_otif_weekly.png)
![EXPLAIN Filtered OTIF](docs/perf_02_explain_analyze_otif_filtered.png)

---
