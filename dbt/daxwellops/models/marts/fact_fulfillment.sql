with o as (
  select * from {{ ref('stg_sales_orders') }}
),
s as (
  select * from {{ ref('stg_shipments') }}
),
agg_ship as (
  select
    order_id,
    min(ship_date) as first_ship_date,
    max(delivered_date) as delivered_date,
    sum(qty_shipped) as qty_shipped_total
  from s
  group by 1
)
select
  o.order_id,
  o.order_date,
  o.customer_id,
  o.sku_id,
  o.qty_ordered,
  coalesce(a.qty_shipped_total, 0) as qty_shipped_total,
  o.promised_ship_date,
  a.first_ship_date,
  a.delivered_date,

  -- In Full: shipped >= ordered
  (coalesce(a.qty_shipped_total, 0) >= o.qty_ordered) as in_full,

  -- On Time: first ship date <= promised ship date
  (a.first_ship_date is not null and a.first_ship_date <= o.promised_ship_date) as on_time,

  -- OTIF: on_time AND in_full
  ((coalesce(a.qty_shipped_total, 0) >= o.qty_ordered)
   and (a.first_ship_date is not null and a.first_ship_date <= o.promised_ship_date)) as otif,

  -- Lead times
  (a.first_ship_date - o.order_date) as order_to_ship_days,
  (a.delivered_date - a.first_ship_date) as ship_to_deliver_days
from o
left join agg_ship a using(order_id)