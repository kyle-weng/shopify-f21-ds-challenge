-- Link to specific questions: https://docs.google.com/document/d/13VCtoyto9X1PZ74nPI4ZEDdb8hF8LAlcmLH1ZTHxKxE/edit#
-- Queries can be run here: https://www.w3schools.com/SQL/TRYSQL.ASP?FILENAME=TRYSQL_SELECT_ALL

-- [Question 2a] Total number of orders shipped by Speedy Express
SELECT SUM(OrderID) AS NumOrders FROM Orders
WHERE ShipperID = (SELECT ShipperID FROM Shippers WHERE ShipperName = "Speedy Express");
-- output: 558777

-- [Question 2b] Last name of employee with most orders
SELECT LastName FROM Employees WHERE EmployeeID =
(SELECT EmployeeID FROM
  (SELECT MAX(NumOrders), EmployeeID FROM
    (SELECT SUM(OrderID) AS NumOrders, EmployeeID FROM Orders GROUP BY EmployeeID ORDER BY NumOrders DESC)
  )
);
-- output: Peacock

-- [Question 2c] Product most ordered by customers in Germany
SELECT ProductName FROM
  (SELECT ProductName, MAX(TotalOrdered) FROM
    (SELECT ProductName, SUM(Quantity) AS TotalOrdered FROM Products NATURAL JOIN Orders NATURAL JOIN OrderDetails
    WHERE CustomerID IN (SELECT CustomerID FROM Customers WHERE Country = "Germany")
    GROUP BY ProductID ORDER BY TotalOrdered DESC)
  )
-- output: Boston Crab Meat