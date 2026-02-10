with o as (
  select * from {{ ref('stg_sales_orders') }}
),
c as (
  select * from {{ ref('stg_contracts') }}
),
joined as (
  select
    o.order_id,
    o.order_date,
    o.customer_id,
    o.sku_id,
    o.qty_ordered,
    o.unit_price as invoiced_price,
    c.agreed_price as contract_price,
    (o.unit_price - c.agreed_price) as price_delta,
    (o.qty_ordered >= c.moq) as moq_ok,
    (o.order_date between c.effective_start and c.effective_end) as effective_date_ok
  from o
  join c
    on o.customer_id = c.customer_id
   and o.sku_id = c.sku_id
   and o.order_date between c.effective_start and c.effective_end
)
select
  *,
  case
    when invoiced_price <> contract_price then 'PRICE_MISMATCH'
    when moq_ok = false then 'MOQ_VIOLATION'
    when effective_date_ok = false then 'DATE_OUT_OF_RANGE'
    else 'OK'
  end as issue_type,
  -- estimated $ impact (positive means overcharge, negative means undercharge)
  round((price_delta * qty_ordered)::numeric, 2) as est_revenue_impact
from joined
where invoiced_price <> contract_price
   or moq_ok = false
   or effective_date_ok = false