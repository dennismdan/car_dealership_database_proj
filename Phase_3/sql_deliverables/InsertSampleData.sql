/******************************/
		--	1.	First Upload sample files
		--	- right click on database name
		--		-Task
		--		-Import Flat File...
		--			-Select file to upload
		--			-Named the table adding sample to the name of the file 
		--				example SamplePerson ,SampleVehicles etc
		--			-On "Modifiying Colums" Step
		--				-Uploading the vehicles file
		--					- Change description and colors to varchar(MAX)
		--					- Change date_aded and sale_date to dateTime
		--				- next and finish
		--				- Change Phones and cst_postal_code to varchar on Person and Business

		--	2.	After uploading all files execute the following script 
		--		to insert data in the corresponding tables

-- Mapping to insert Sample data into schema

--INSERT INTO USER
INSERT INTO EmployeeUser
SELECT DISTINCT
	s.username
	,s.password
	,s.u_f_name
	,s.u_l_name
	,s.roles
FROM SampleUsers s
WHERE NOT EXISTS (SELECT t.username
					FROM EmployeeUser t
					WHERE t.username = s.username)

--INSERT INTO MANUFACTURER
INSERT INTO Manufacturer
SELECT DISTINCT manufacturer_name 
FROM SampleVehicles s 
WHERE NOT EXISTS
	(SELECT manufacturer_name 
	FROM Manufacturer m 
	WHERE s.manufacturer_name = m.manufacturer_name)


--INSERT VECHILES
--select * from vehicle
INSERT INTO Vehicle (VIN,Year,Model_name,Description,Invoice_price,Inventory_date,Manufacturer_name,Username)
SELECT 
	s.VIN
	,s.year
	,s.model
	,s.description
	--,s.invoice_price*1.25
	,s.invoice_price
	,s.date_added
	,s.manufacturer_name
	,s.added_by
FROM SampleVehicles s
WHERE NOT EXISTS(SELECT t.VIN 
				FROM Vehicle t
				WHERE s.VIN=t.VIN)


-- INSERT CAR 
--select * from car
--select * from SampleVehicles

INSERT INTO Car (VIN, Doors_count)
SELECT
	s.VIN
	,s.number_doors
FROM SampleVehicles s
WHERE s.vehicle_type = 'Car'
AND NOT EXISTS( SELECT t.VIN FROM Car t WHERE s.VIN=t.VIN)

-- INSERT CONVERTIBLE
--select * from CONVERTIBLE
--select * from SampleVehicles

INSERT INTO Convertible (VIN,Roof_type,Back_seat_count)
SELECT
	s.VIN
	,s.roof_type
	,s.back_seat_count
FROM SampleVehicles s
WHERE s.vehicle_type = 'Convertible'
AND NOT EXISTS( SELECT t.VIN FROM Convertible t WHERE s.VIN=t.VIN)



-- INSERT SUV
--select * from SUV
--select * from SampleVehicles

INSERT INTO SUV (VIN,Drivetrain_type,Cupholder_count)
SELECT
	s.VIN
	,s.drive_train_type
	,s.num_cupholders
FROM SampleVehicles s
WHERE s.vehicle_type = 'SUV'
AND NOT EXISTS( SELECT t.VIN FROM SUV t WHERE s.VIN=t.VIN)


-- INSERT TRUCK
--select * from Truck
--select * from SampleVehicles

INSERT INTO Truck (VIN,Cargo_capacity,Cargo_cover_type,Axle_count)
SELECT
	s.VIN
	,s.capacity
	,s.cover_type
	,num_rear_axles
FROM SampleVehicles s
WHERE s.vehicle_type = 'Truck'
AND NOT EXISTS( SELECT t.VIN FROM Truck t WHERE s.VIN=t.VIN)


-- INSERT VANMINIVAN
--select * from VanMinivan
--select * from SampleVehicles

INSERT INTO VanMinivan(VIN,Has_driver_back_door)
SELECT
	s.VIN
	,s.driver_side_door
FROM SampleVehicles s
WHERE s.vehicle_type = 'Van'
AND NOT EXISTS( SELECT t.VIN FROM VanMinivan t WHERE s.VIN=t.VIN)


/*********************************************************/
-- validation
/*********************************************************/

--select * from car where len(VIN)>10  --101
--select * from SampleVehicles where vehicle_type = 'car' --101

--select * from Convertible where len(VIN)>10  --102
--select * from SampleVehicles where vehicle_type = 'convertible' --102

--select * from SUV where len(VIN)>10  --122
--select * from SampleVehicles where vehicle_type = 'Suv' --122

--select * from Truck where len(VIN)>10  --90
--select * from SampleVehicles where vehicle_type = 'Truck' --90

--select * from VanMinivan where len(VIN)>10  --85
--select * from SampleVehicles where vehicle_type = 'Van' --85

--SELECT 101+102+122+90+85 --500


--INSERT COLOR
--SELECT * FROM Color
--SELECT * FROM SampleVehicles

INSERT INTO COLOR(VIN,Color)
SELECT VIN, value
FROM SampleVehicles
	CROSS APPLY string_split(colors,',')


-- INSERT BUSINESS INTO CUSTOMER TABLE FIRST
--SELECT * FROM Business
--SELECT * FROM SampleBusiness
--SELECT * FROM Customer

INSERT INTO Customer (Phone_number,Email,Street_address,City,State,Postal_code) 
SELECT
	s.phone
	,s.email
	,s.cst_street_addr
	,s.cst_city
	,s.cst_state
	,s.cst_postal_code
FROM SampleBusiness s


--INSERT BUSINESS
--select * from business
INSERT INTO Business(TIN,Customer_id,Contact_name,Contact_title,Business_name)
SELECT
	s.tax_num
	,c.Customer_id
	,s.c_f_name + ' ' + s.c_l_name
	,s.c_title
	,s.bzn_name
FROM SampleBusiness s
LEFT JOIN Customer c ON s.phone =c.Phone_number



--INSERT PERSON INTO CUSTOMER TABLE FIRST
--SELECT * FROM Customer
--SELECT * FROM SamplePerson

INSERT INTO Customer (Phone_number,Email,Street_address,City,State,Postal_code) 
SELECT
	s.phone
	,s.email
	,s.cst_street_addr
	,s.cst_city
	,s.cst_state
	,s.cst_postal_code
FROM SamplePerson s




--INSERT person
--select * from person
--select * from SamplePerson

INSERT INTO Person(Driver_license,Customer_id,First_name,Last_name)
SELECT
	s.driver_lic
	,c.Customer_id
	,s.p_f_name 
	,s.p_l_name
FROM SamplePerson s
LEFT JOIN Customer c ON s.phone =c.Phone_number



-- INSERT Repair
--select * from Repair
--select * from SampleRepairs

INSERT INTO Repair(VIN,Customer_id,Start_date,Labor_charges,Description,Completion_date,Odometer_reading,Username)
SELECT 
	s.VIN
	,c.Customer_id
	,start_date
	,s.labor_cost
	--,totalcost
	,s.repair_desc
	,s.completion_date
	,s.odometer
	,s.service_writer
FROM SampleRepairs s
LEFT JOIN 
(
SELECT TIN AS customer, Customer_id from Business
UNION
SELECT Driver_license as Customer,Customer_id FROM Person
) AS c ON c.customer = s.customer




--INSERT PART
--SELECT * FROM PART
--select * from SampleRepairs
--select * from SampleParts

INSERT INTO Part (VIN,Customer_id,Start_date,Part_number,Vendor_name,Quantity,Price)
SELECT 
	s.VIN
	,c.Customer_id
	,s.start_date
	,s.pt_number
	,s.vendor_name
	,s.quantity
	,s.pt_price
	--,s.labor_cost
	--,totalcost
	--,s.repair_desc
	--,s.completion_date
	--,s.odometer
	--,s.service_writer
FROM SampleParts s
LEFT JOIN SampleRepairs sr ON s.VIN=sr.VIN and s.start_date=sr.start_date
LEFT JOIN 
(
SELECT TIN AS customer, Customer_id from Business
UNION
SELECT Driver_license as Customer,Customer_id FROM Person
) AS c ON c.customer = sr.customer

--insert SALE
--select * from Sale
--select * from SampleVehicles WHERE sale_date IS NOT NULL

INSERT INTO Sale (VIN,Username,Customer_id,Sale_price,Sale_date)
SELECT
	s.VIN
	,s.sold_by
	,c.customer_id
	,s.sold_price
	,s.sale_date
	--,c.*
FROM SampleVehicles s
LEFT JOIN (
			SELECT TIN AS customer, Customer_id from Business
			UNION
			SELECT Driver_license as Customer,Customer_id FROM Person
			) AS c ON c.customer = s.customer
WHERE s.sale_date IS NOT NULL

--update total cost on repair table
UPDATE REPAIR SET Total_cost = isnull(s.PartsCost,'0') + r.Labor_charges
from Repair r
LEFT JOIN (SELECT p.VIN ,p.Customer_id,p.start_date, sum(p.Price*p.Quantity) AS PartsCost
			FROM Part p group by p.VIN ,p.Customer_id,p.start_date) as s
			ON r.vin=s.vin and r.Customer_id=s.Customer_id and r.Start_date=s.Start_date
			WHERE r.VIN = '$VIN'
			and r.Customer_id = '$Customer_id'
			and r.Start_date = '$Start_date '


