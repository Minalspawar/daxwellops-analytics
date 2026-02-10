create schema if not exists raw;
create schema if not exists analytics;

create table if not exists raw.sales_orders (
  order_id text primary key,
  order_date date,
  customer_id text,
  sku_id text,
  qty_ordered int,
  unit_price numeric(10,2),
  promised_ship_date date
);

create table if not exists raw.contracts (
  customer_id text,
  sku_id text,
  agreed_price numeric(10,2),
  moq int,
  effective_start date,
  effective_end date,
  primary key (customer_id, sku_id, effective_start)
);

create table if not exists raw.shipments (
  shipment_id text primary key,
  order_id text,
  ship_date date,
  delivered_date date,
  qty_shipped int,
  carrier text,
  warehouse text,
  priority text
);

create table if not exists raw.inventory_snapshots (
  snapshot_date date,
  sku_id text,
  on_hand_qty int,
  on_order_qty int
);

create table if not exists raw.production_batches (
  batch_id text primary key,
  production_date date,
  sku_id text,
  line text,
  shift text,
  qty_produced int,
  scrap_qty int
);