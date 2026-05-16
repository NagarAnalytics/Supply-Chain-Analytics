USE SupplyChainDB;
/* EXEC sp_help 'Sales'; 
-- Or
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Sales' AND COLUMN_NAME = 'Revenue_USD'; */

--ALTER TABLE Sales
--ALTER COLUMN Revenue_USD DECIMAL(18,2);

--SELECT SUM(CASE WHEN Revenue_USD IS NULL THEN 1 ELSE 0 END) AS null_count FROM Sales;
 
/*
-- 1. Customers
CREATE TABLE Customers (
    CustomerKey     INT PRIMARY KEY,
    Gender          VARCHAR(20),
    Name            VARCHAR(200),
    City            VARCHAR(200),
    State_Code      VARCHAR(20),
    State           VARCHAR(200),
    Country         VARCHAR(200),
    Continent       VARCHAR(100),
    Birthday        DATE,
    Age             INT,
);

-- 2. Products
CREATE TABLE Products (
    ProductKey          INT PRIMARY KEY,
    Product_Name        VARCHAR(500),
    Brand               VARCHAR(200),
    Color               VARCHAR(100),
    Unit_Cost_USD       DECIMAL(10,2),
    Unit_Price_USD      DECIMAL(10,2),
    SubcategoryKey      INT,
    Subcategory         VARCHAR(200),
    CategoryKey         INT,
    Category            VARCHAR(200),
    Profit_Margin       DECIMAL(10,4),
    Price_Check         VARCHAR(50)
);

-- 3. Stores
CREATE TABLE Stores (
    StoreKey        INT PRIMARY KEY,
    Country         VARCHAR(200),
    State           VARCHAR(200),
    Square_Meters   DECIMAL(10,2),
    Open_Date       DATE,
    Store_Age_Years INT
);

-- 4. Exchange_Rates
CREATE TABLE Exchange_Rates (
    Exchange_Date   DATE,
    Currency        VARCHAR(20),
    Exchange        DECIMAL(10,6),
    PRIMARY KEY (Exchange_Date, Currency)
);

-- 5. Sales
CREATE TABLE Sales (
    Order_Number            VARCHAR(100),
    Line_Item               INT,
    Order_Date              DATE,
    Delivery_Date           DATE,
    CustomerKey             INT,
    StoreKey                INT,
    ProductKey              INT,
    Quantity                INT,
    Currency_Code           VARCHAR(20),
    Delivery_Delay_Days     INT,
    Delivery_Status         VARCHAR(50),
    Sales_Channel           VARCHAR(50),
    Revenue_USD             DECIMAL(10,2),
    PRIMARY KEY (Order_Number, Line_Item),
    FOREIGN KEY (CustomerKey)   REFERENCES Customers(CustomerKey),
    FOREIGN KEY (StoreKey)      REFERENCES Stores(StoreKey),
    FOREIGN KEY (ProductKey)    REFERENCES Products(ProductKey)
);

-- 6. OrderList
CREATE TABLE OrderList (
    Order_ID                VARCHAR(100) PRIMARY KEY,
    Order_Date              DATE,
    Origin_Port             VARCHAR(200),
    Carrier                 VARCHAR(200),
    TPT                     INT,
    Service_Level           VARCHAR(50),
    Ship_Ahead_Day_Count    INT,
    Ship_Late_Day_Count     INT,
    Customer                VARCHAR(200),
    Product_ID              VARCHAR(100),
    Plant_Code              VARCHAR(100),
	Destination_Port        VARCHAR(200),
    Unit_Quantity           INT,
    Weight                  DECIMAL(10,2),
    On_Time_Status          VARCHAR(50),
    Total_Delay_Days        INT
	
);

-- 7. FreightRates
CREATE TABLE FreightRates (
    Carrier             VARCHAR(200),
    Origin_Port         VARCHAR(200),
    Destination_Port    VARCHAR(200),
    Min_Wgh_Qty         DECIMAL(10,2),
    Max_Wgh_Qty         DECIMAL(10,2),
    SVC                 VARCHAR(50),
    Rate                DECIMAL(10,4),
    Minimum_Cost        DECIMAL(10,2)
	Mode				VARCHAR(50)
);

-- 8. PlantPorts
CREATE TABLE PlantPorts (
    Plant_Code  VARCHAR(100) PRIMARY KEY,
    Port        VARCHAR(200)
);

-- 9. ProductsPerPlant
CREATE TABLE ProductsPerPlant (
    Plant_Code  VARCHAR(100),
    Product_ID  VARCHAR(100),
    PRIMARY KEY (Plant_Code, Product_ID)
);

-- 10. WhCapacities
CREATE TABLE WhCapacities (
    Plant_ID        VARCHAR(100) PRIMARY KEY,
    Daily_Capacity  INT
);

-- 11. WhCosts
CREATE TABLE WhCosts (
    Warehouse   VARCHAR(100) PRIMARY KEY,
    Cost_Unit   DECIMAL(10,4)
);
*/


/*
-- Drop all tables in correct order (reverse of creation)
DROP TABLE IF EXISTS Sales;
DROP TABLE IF EXISTS OrderList;
DROP TABLE IF EXISTS ProductsPerPlant;
DROP TABLE IF EXISTS FreightRates;
DROP TABLE IF EXISTS WhCosts;
DROP TABLE IF EXISTS WhCapacities;
DROP TABLE IF EXISTS PlantPorts;
DROP TABLE IF EXISTS Exchange_Rates;
DROP TABLE IF EXISTS Stores;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;
*/

--INSERT INTO OrderList
--SELECT * FROM OrderList;

--DROP TABLE OrderList_s; 

--ALTER TABLE Sales NOCHECK CONSTRAINT ALL;

--ALTER TABLE Sales CHECK CONSTRAINT ALL;


--DROP TABLE IF EXISTS OrderList;

--SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
--FROM INFORMATION_SCHEMA.COLUMNS;


/*-- Check 3: Row counts for all tables
SELECT 'Customers'        AS TableName, COUNT(*) AS Rows FROM Customers       UNION ALL
SELECT 'Products'         AS TableName, COUNT(*) AS Rows FROM Products        UNION ALL
SELECT 'Stores'           AS TableName, COUNT(*) AS Rows FROM Stores          UNION ALL
SELECT 'Exchange_Rates'   AS TableName, COUNT(*) AS Rows FROM Exchange_Rates  UNION ALL
SELECT 'Sales'            AS TableName, COUNT(*) AS Rows FROM Sales           UNION ALL
SELECT 'OrderList'        AS TableName, COUNT(*) AS Rows FROM OrderList       UNION ALL
SELECT 'FreightRates'     AS TableName, COUNT(*) AS Rows FROM FreightRates    UNION ALL
SELECT 'PlantPorts'       AS TableName, COUNT(*) AS Rows FROM PlantPorts      UNION ALL
SELECT 'ProductsPerPlant' AS TableName, COUNT(*) AS Rows FROM ProductsPerPlant UNION ALL
SELECT 'WhCapacities'     AS TableName, COUNT(*) AS Rows FROM WhCapacities    UNION ALL
SELECT 'WhCosts'          AS TableName, COUNT(*) AS Rows FROM WhCosts; */


------------------------------8 key business queries-------------------------------

-- 1. What is the overall On-Time Delivery Rate?

/*SELECT  
		On_Time_Status,
		COUNT(*) AS OrderCount,
		CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS Decimal(5, 2)) AS Percentage
FROM OrderList
--WHERE On_Time_Status = 'On Time'
GROUP BY On_Time_Status
ORDER BY OrderCount DESC */


-- 2. Which carriers have the worst delays?

/* SELECT 
		Carrier,
		SUM(Total_Delay_Days) AS Total_Delay_Days_Sum
FROM OrderList
WHERE On_Time_Status = 'Late'
GROUP BY Carrier
ORDER BY Total_Delay_Days_Sum DESC */


-- 3. What is revenue by product category?

/*SELECT  
		p.Category, 
		SUM(s.Revenue_USD) AS CategoryRevenue
		
FROM Sales s
JOIN Products p on s.ProductKey = p.ProductKey
GROUP BY p.Category
ORDER BY CategoryRevenue DESC


--FORMAT function 
SELECT 
    p.Category, 
    FORMAT(SUM(s.Revenue_USD), 'C', 'en-US') AS CategoryRevenue
FROM Sales s
JOIN Products p ON s.ProductKey = p.ProductKey
GROUP BY p.Category
ORDER BY SUM(s.Revenue_USD) DESC; */


-- 4 Which regions generate the most revenue?

/*SELECT 
		--TOP 5
		c.Continent,
		SUM(s.Revenue_USD) as Total_Revenue
FROM Sales s
JOIN Customers c on s.CustomerKey = c.CustomerKey
GROUP BY c.Continent
ORDER BY Total_Revenue DESC */


--5. What is the monthly order trend?
/*
SELECT 

		FORMAT(Order_Date, 'MMMM') AS 'Month',
		COUNT(Order_Number) AS Total_Orders,
		SUM(Revenue_USD) AS Monthly_revenue

FROM Sales 
GROUP BY FORMAT(Order_Date, 'MMMM')
ORDER BY Monthly_revenue DESC


SELECT 
    FORMAT(Order_Date, 'yyyy') AS [Year],
    FORMAT(Order_Date, 'MMMM') AS [Month],
    SUM(Revenue_USD) AS Monthly_revenue
FROM Sales
GROUP BY 
    FORMAT(Order_Date, 'yyyy'), 
    FORMAT(Order_Date, 'MMMM')
ORDER BY [Year] DESC, Monthly_revenue DESC;


SELECT 
    FORMAT(Order_Date, 'MMMM') AS 'Month',
    COUNT(Order_Number) AS Total_Orders,
    SUM(Revenue_USD) AS Monthly_revenue
FROM Sales
GROUP BY FORMAT(Order_Date, 'MMMM')
ORDER BY MONTH(MIN(Order_Date)) ASC; -- This puts them in Jan, Feb, Mar order */

--6. Which products have the highest profit margin?
/*
SELECT 
    ProductKey,
    Product_Name,
    FORMAT(MAX(Profit_Margin), 'P') AS 'Margin_Percentage'
FROM Products
GROUP BY ProductKey, Product_Name
ORDER BY MAX(Profit_Margin) DESC; */

--7. What is the warehouse cost vs capacity efficiency?
/*
SELECT 
    wc.Plant_ID,
    wc.Daily_Capacity,
    wt.Cost_Unit,
    CAST(wc.Daily_Capacity * wt.Cost_Unit 
        AS DECIMAL(10,2))               AS Daily_Cost,
    CAST(wt.Cost_Unit / wc.Daily_Capacity 
        AS DECIMAL(10,4))               AS Cost_Per_Unit
FROM WhCapacities wc
JOIN WhCosts wt ON wc.Plant_ID = wt.Warehouse
ORDER BY Cost_Per_Unit ASC; */


--8. Online vs In-Store Performance
/*
SELECT 
    Sales_Channel,
    COUNT(Order_Number)                 AS Total_Orders,
    COUNT(DISTINCT CustomerKey)         AS Unique_Customers,
    FORMAT(SUM(Revenue_USD), 'C', 
        'en-US')                        AS Total_Revenue,
    FORMAT(AVG(Revenue_USD), 'C', 
        'en-US')                        AS Avg_Order_Value
FROM Sales
GROUP BY Sales_Channel
ORDER BY SUM(Revenue_USD) DESC; */

-- Advanced Query 1: Year over Year Revenue Growth
WITH YearlyRevenue AS (
    SELECT 
        YEAR(Order_Date)            AS Year,
        SUM(Revenue_USD)            AS Total_Revenue
    FROM Sales
    GROUP BY YEAR(Order_Date)
)
SELECT 
    Year,
    FORMAT(Total_Revenue, 'C', 'en-US')     AS Total_Revenue,
    FORMAT(LAG(Total_Revenue) OVER 
        (ORDER BY Year), 'C', 'en-US')      AS Prev_Year_Revenue,
    FORMAT((Total_Revenue - LAG(Total_Revenue) OVER(ORDER BY Year)) / 
        LAG(Total_Revenue) 
        OVER(ORDER BY Year) * 100, 
        'N2')                               AS YoY_Growth_Pct
FROM YearlyRevenue
ORDER BY Year;

-- Advanced Query 2: Customer Segmentation by Revenue
WITH CustomerRevenue AS (
    SELECT 
        s.CustomerKey,
        c.Name,
        c.Country,
        SUM(s.Revenue_USD)          AS Total_Revenue,
        COUNT(s.Order_Number)       AS Total_Orders
    FROM Sales s
    JOIN Customers c ON s.CustomerKey = c.CustomerKey
    GROUP BY s.CustomerKey, c.Name, c.Country
)
SELECT 
    CustomerKey,
    Name,
    Country,
    FORMAT(Total_Revenue, 'C', 'en-US')     AS Total_Revenue,
    Total_Orders,
    CASE 
        WHEN Total_Revenue >= 10000 THEN 'Premium'
        WHEN Total_Revenue >= 5000  THEN 'High Value'
        WHEN Total_Revenue >= 1000  THEN 'Medium Value'
        ELSE 'Low Value'
    END                                     AS Customer_Segment
FROM CustomerRevenue
ORDER BY Total_Revenue DESC;

-- Advanced Query 3: Product Performance Ranking within Category
SELECT 
    p.Category,
    p.Product_Name,
    FORMAT(SUM(s.Revenue_USD), 'C', 
        'en-US')                            AS Product_Revenue,
    RANK() OVER (
        PARTITION BY p.Category 
        ORDER BY SUM(s.Revenue_USD) DESC)   AS Rank_In_Category,
    FORMAT(SUM(s.Revenue_USD) * 100.0 / 
        SUM(SUM(s.Revenue_USD)) 
        OVER(PARTITION BY p.Category), 
        'N2')                               AS Pct_Of_Category
FROM Sales s
JOIN Products p ON s.ProductKey = p.ProductKey
GROUP BY p.Category, p.Product_Name
ORDER BY p.Category, Rank_In_Category;

--9. Which suppliers are causing the most delays?

