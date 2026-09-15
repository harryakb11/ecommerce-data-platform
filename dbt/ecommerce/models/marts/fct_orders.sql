SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    gross_amount,
    status
FROM {{ ref('int_orders') }}
WHERE status != 'cancelled'