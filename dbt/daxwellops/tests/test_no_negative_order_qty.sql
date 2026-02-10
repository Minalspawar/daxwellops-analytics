select *
from {{ ref('stg_sales_orders') }}
where qty_ordered <= 0