with src as (
  select * from raw.sales_orders
)
select
  order_id,
  order_date,
  customer_id,
  sku_id,
  qty_ordered,
  unit_price,
  promised_ship_date
from src