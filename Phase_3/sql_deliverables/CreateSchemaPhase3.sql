--********************************************************************
-- Phase 3 Schema  | CS 6400 – Fall 2021 | Team 081
-- =============================================
-- Author:			Mauricio Piraquive
-- Create Date:		11-30-2021
-- Description:		Create schema
-- =============================================
-- Summary of changes
-- Date             Author		Description
-- 11-30-2021		MP			Change of TIN and driver license to varchar(50) on Person and Business Tables
-- 11-30-2021		MP			Change of List_price AS Invoice_price*1.25
-- 11-30-2021		MP			Change of Part Number to Varchar(50) on table Part
-- =============================================

--********************************************************************

CREATE TABLE   EmployeeUser (
    Username  VARCHAR(50) NOT NULL,
    Password  VARCHAR(60) NOT NULL,
    First_name  VARCHAR(100) NOT NULL,
	Last_name	VARCHAR(100) NOT NULL,
    Job_type  VARCHAR (100) NOT NULL,
    PRIMARY KEY (Username)
);

CREATE TABLE Manufacturer (
Manufacturer_name VARCHAR(50) NOT NULL,
PRIMARY KEY(Manufacturer_name)
);

CREATE TABLE Customer (
Customer_id INTEGER IDENTITY(1,1) PRIMARY KEY, -- Artificial Identifier for UNION
Phone_number VARCHAR(50) NOT NULL,
Email VARCHAR(50) NULL,
Street_address VARCHAR(100) NOT NULL,
City VARCHAR(50) NOT NULL,
State VARCHAR(50) NOT NULL,
Postal_code VARCHAR(50) NOT NULL
);

CREATE TABLE Vehicle (
VIN VARCHAR (50) NOT NULL,
Year INTEGER NOT NULL,
Model_name VARCHAR(50) NOT NULL,
Description VARCHAR(250) NULL,
Invoice_price FLOAT(24) NOT NULL,
List_price AS Invoice_price*1.25,
Inventory_date DATETIME NOT NULL,
Manufacturer_name VARCHAR(50) NOT NULL,
Username  VARCHAR (50) NOT NULL,
PRIMARY KEY(VIN),
FOREIGN KEY (Manufacturer_name) REFERENCES Manufacturer(Manufacturer_name),
FOREIGN KEY (Username) REFERENCES EmployeeUser(Username)
);

CREATE TABLE Color (
VIN VARCHAR (50) NOT NULL,
Color  VARCHAR(50) NOT NULL,
PRIMARY KEY(VIN,Color),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN)
);

CREATE TABLE Car (
VIN VARCHAR (50) NOT NULL,
Doors_count INT NOT NULL,
PRIMARY KEY(VIN),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN)
);

CREATE TABLE Convertible (
VIN VARCHAR(50) NOT NULL,
Roof_type VARCHAR(50) NOT NULL,
Back_seat_count INT NOT NULL,
PRIMARY KEY(VIN),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN)
);

CREATE TABLE Truck (
VIN VARCHAR (50) NOT NULL,
Cargo_capacity FLOAT NOT NULL,
Cargo_cover_type VARCHAR(50) NULL,
Axle_count INT NOT NULL,
PRIMARY KEY (VIN),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN)
);

CREATE TABLE VanMinivan (
VIN VARCHAR(50) NOT NULL,
Has_driver_back_door BIT NOT NULL, --1 FOR yes 0 for NO
PRIMARY KEY(VIN),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN)
);

CREATE TABLE SUV (
VIN VARCHAR (50) NOT NULL,
Drivetrain_type VARCHAR(50) NOT NULL,
Cupholder_count INT NOT NULL,
PRIMARY KEY (VIN),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN)
);

CREATE TABLE Person(
Driver_license VARCHAR(50) NOT NULL,
Customer_id INTEGER NOT NULL, 
First_name VARCHAR(50) NOT NULL,
Last_name VARCHAR(50) NOT NULL,
PRIMARY KEY (Driver_license),
FOREIGN KEY(Customer_id) REFERENCES Customer(Customer_id)
);


CREATE TABLE Business(
TIN VARCHAR(50) NOT NULL,
Customer_id INTEGER NOT NULL,
Contact_name VARCHAR(50) NOT NULL, 
Contact_title VARCHAR(50) NOT NULL,
Business_name VARCHAR(50) NOT NULL,
PRIMARY KEY (TIN),
FOREIGN KEY(Customer_id) REFERENCES Customer(Customer_id)
);


CREATE TABLE Sale(
VIN VARCHAR (50) NOT NULL,
Username  VARCHAR (50) NOT NULL,
Customer_id INTEGER NOT NULL,
Sale_price FLOAT NOT NULL,
Sale_date DATETIME NOT NULL,
PRIMARY KEY (VIN,Username,Customer_id),
FOREIGN KEY(VIN) REFERENCES Vehicle(VIN),
FOREIGN KEY(Username) REFERENCES EmployeeUser(Username),
FOREIGN KEY(Customer_id) REFERENCES Customer(Customer_id)
);


CREATE TABLE Repair (
VIN VARCHAR (50) NOT NULL,
Customer_id INTEGER NOT NULL,
Start_date DATETIME NOT NULL,
Labor_charges FLOAT NULL,
Total_cost FLOAT NULL,
Description VARCHAR(500) NOT NULL,
Completion_date DATETIME NULL,
Odometer_reading INTEGER NOT NULL,
Username VARCHAR(50) NOT NULL,
PRIMARY KEY(VIN,Start_date,Customer_id),
FOREIGN KEY(VIN) REFERENCES Vehicle (VIN),
FOREIGN KEY(Customer_id) REFERENCES Customer(Customer_id),
CHECK(Completion_date>=Start_date)
);


CREATE TABLE Part(
VIN VARCHAR (50) NOT NULL,
Customer_id INT NOT NULL,
Start_date DATETIME NOT NULL,
Part_number VARCHAR(50) NOT NULL,
Vendor_name VARCHAR(100) NULL,
Quantity INT NOT NULL,
Price FLOAT NOT NULL,
PRIMARY KEY(VIN,Customer_id,Start_date,Part_number),
FOREIGN KEY(VIN,Start_date,Customer_id) REFERENCES Repair(VIN,Start_date,Customer_id)
);