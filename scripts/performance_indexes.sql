-- Performance indexes for common analytics filters/joins
-- Raw layer
create index if not exists idx_raw_sales_orders_order_date on raw.sales_orders(order_date);
create index if not exists idx_raw_sales_orders_customer_id on raw.sales_orders(customer_id);
create index if not exists idx_raw_sales_orders_sku_id on raw.sales_orders(sku_id);

create index if not exists idx_raw_shipments_order_id on raw.shipments(order_id);
create index if not exists idx_raw_shipments_ship_date on raw.shipments(ship_date);

-- Analytics marts (Metabase queries hit these most)
create index if not exists idx_fact_fulfillment_order_date on analytics.fact_fulfillment(order_date);
create index if not exists idx_fact_fulfillment_customer_id on analytics.fact_fulfillment(customer_id);
create index if not exists idx_fact_fulfillment_sku_id on analytics.fact_fulfillment(sku_id);

create index if not exists idx_fact_contract_violations_issue_type on analytics.fact_contract_violations(issue_type);
create index if not exists idx_fact_contract_violations_order_date on analytics.fact_contract_violations(order_date);