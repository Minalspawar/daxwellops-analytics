select
  shipment_id,
  order_id,
  ship_date,
  delivered_date,
  qty_shipped,
  carrier,
  warehouse,
  priority
from raw.shipments