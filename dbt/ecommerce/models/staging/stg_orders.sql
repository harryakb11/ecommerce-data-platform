SELECT
    order_id,
    CAST(order_date AS DATE) AS order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    status
FROM {{ source('raw', 'orders') }}