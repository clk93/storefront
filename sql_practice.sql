select * from store_orderitem;
select * from store_orderitem as oi 
join store_order as o on o.id = oi.id 
join store_customer as c on o.customer_id = c.id
join store_product as p on oi.product_id = p.id
order by placed_at limit 5; 