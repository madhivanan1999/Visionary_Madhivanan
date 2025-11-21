--==================Part A: Data Cleaning & Exploration==================--

select count([order id]) as total_order_count from [Order]
select count([Product id]) as total_product_count from product_info
select count(Returned) as total_returned_count from [return]
select count(Segment) as total_people_count from people_info

select *from [order] t1
left join Product_info t2 
on t1.[Product ID] = t2.[Product ID] 
left join [Return] t3
on t1.[Order ID] = t3.[Order ID]
left join People_info t4
on t1.[Customer ID] = t4.[Customer ID]

--1. Load all sheets into SSMS and explore the data.

-- order and product_info table lookup(left join)
alter table [order]
add category varchar(50), [sub-category] varchar(50), [product name] varchar(200)
update o
set o.category = pr.category, o.[sub-category] = pr.[sub-category], o.[product name] = pr.[product name]
from [order] o left join [Product_info] pr on o.[Product ID] = pr.[Product ID]

--order and Retun table lookup(left join)
alter table [order]
add returned varchar(10)
update o 
set o.returned = r.returned 
from [order] o left join [return] r on o.[order id] = r.[order id]

--2. Remove duplicates in the Orders sheet
select [Order ID],[Customer ID],[customer name],[postal code] , [Product ID], count(*) as duplicate from [order]
group by [row id],[Order ID], [Customer ID],[customer name],[postal code],[Product ID]
having count(*) > 1

--3. Check for missing values in each sheet
select *from [order]
where [Order Date] is null

--4. Convert Order Date and Ship Date into proper Date format.
select convert(date, [order date], 103) as order_date, --YYYY/MM/DD
convert(date, [ship date], 103) as ship_date
from [order]

--5. Create a column to 
alter table [order]
add shipping_date int
--calculate Shipping Days (Ship Date – Order Date).
update [order] 
set shipping_date = datediff(day, convert(date, [order date],103), convert(date, [ship date], 103))


--=======================Part B: Basic Analysis====================--

--6. Find total sales, total profit, and total quantity overall.
select sum(cast(sales as float)) as Total_Sales  from [order] --Total_Sales
select sum(cast(profit as float)) as Total_Profit from [order] --Total_Profit
select sum(cast(quantity as int)) as Total_quantity from [order] --Total_quantity

--7. Calculate average discount and average profit margin.
select avg(cast(discount as float)) as Average_Discount from [order] --Average_Discount

with pro_mar as (
select cast(profit as float) as profits, cast(sales as float) as sale , 
cast(profit as float)/cast(sales as float)*100 as profit_margin from [order]
)
select avg(profit_margin) as average_profit_margin from pro_mar

--8. Showing Sales & Profit by Region.
select region, sum(cast(sales as float)) as Total_sales, sum(cast(profit as float)) as Total_profit 
from [order]
group by region

--9. Showing Sales by Category and Sub-Category.
select category, [sub-category], sum(cast(sales as float)) as Total_sales
from [order]
group by category, [sub-category]
order by category

--10. Identify the Top 10 customers by Sales.
select top 10 [customer id], [customer name],sales from [order]
order by cast(sales as float) desc


--=======================Part C: Intermediate Analysis====================--

--11. Find the % of returned orders
select [order id], count(*) as duplicates from [order]
group by [order id]
having count(*) > 1 --if i remove the duplicate Order id's, it will affect the whole table

--12. Analyze Sales by Category
select category, sum(cast(sales as float)) sales_by_category from [order] 
group by category

--13. Calculate Profit per Order and find the Most profitable order
alter table [order]
add profit_per_order float

update [order]
set profit_per_order = 
case 
when cast(quantity as int) = 0 then null
else cast(profit as float)/cast(quantity as int)
end ----------Profit per Order

select top 1 [customer id], [customer name],profit_per_order from [order]
order by cast(profit_per_order as float) desc  -- --find the Most profitable order

--=======================Part D: Advanced Analysis=======================--

--16. Segment customers based on total sales into Gold, Silver, Bronze.
alter table [order]
add customer_seg varchar(50)

update [order]
set customer_seg = case when cast(sales as float) <= 10000 then 'Bronze'
when cast(sales as float) <= 17000 then 'Silver'
else 'Gold' end

--17. Calculate Year-over-Year Sales Growth.
select year(convert(date, [order date], 103)) as year_over_year , sum(cast(sales as float)) as Total_sales from [order]
group by year(convert(date, [order date], 103))
order by year_over_year

--=======================Bonus Challenge=======================--

--19. Customer Segment
select segment, [customer id], [customer name] from [order]
order by segment

--20. Identify products with negative profit and suggest whether to discontinue them.
alter table [order]
add sugg_discontinue_or_not varchar(50)

update [order]
set sugg_discontinue_or_not = case when cast(profit as float) <= -300 then 'discontinue'
else 'not_discontinue'
end

select *from [order]