ALTER TABLE users ADD COLUMN user_type ENUM('EMPLOYEE', 'CUSTOMER', 'BOOKING-AGENT', 'VENDOR', 'CONTRACTOR', 'PARTNER', 'CXO', 'COMPANY', 'BACK-OFFICE') NOT NULL DEFAULT 'EMPLOYEE';
ALTER TABLE users ADD COLUMN area VARCHAR(250);
ALTER TABLE users ADD COLUMN city VARCHAR(50);
ALTER TABLE users ADD COLUMN state VARCHAR(50);
ALTER TABLE users ADD COLUMN country VARCHAR(50);
ALTER TABLE users ADD COLUMN zip_code VARCHAR(10);

----------------------------------------------------------------------
-- Backup customers and bookings before migration
CREATE TABLE customers_backup AS SELECT * FROM customers;
CREATE TABLE bookings_backup AS SELECT * FROM bookings;

CREATE TABLE customer_user_mapping (
    old_customer_id INT PRIMARY KEY,
    new_user_id INT NOT NULL,
    FOREIGN KEY (new_user_id) REFERENCES users(user_id)
);

ALTER TABLE bookings DROP FOREIGN KEY ; --- customer_id
-----------------

INSERT INTO users (
    username, password, first_name, last_name, email, phone,
    booking_commission, user_type, area, city, state, country, zip_code
)
SELECT 
    CONCAT('cust_', customer_id) AS username,
    'no-password' AS password,  -- you can later reset passwords or leave dummy
    SUBSTRING_INDEX(full_name, ' ', 1) AS first_name,
    TRIM(SUBSTRING(full_name, LOCATE(' ', full_name))) AS last_name,
    email,
    phone,
    0 AS booking_commission,
    'CUSTOMER' AS user_type,
    area, city, state, country, zip_code
FROM customers;

INSERT INTO customer_user_mapping (old_customer_id, new_user_id)
SELECT c.customer_id, u.user_id
FROM customers c
JOIN users u ON u.username = CONCAT('cust_', c.customer_id);

 
UPDATE bookings b
JOIN customer_user_mapping m ON b.customer_id = m.old_customer_id
SET b.customer_id = m.new_user_id;

ALTER TABLE bookings
    ADD CONSTRAINT fk_bookings_customer_id FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_bookings_source_id FOREIGN KEY (source_of_booking_id) REFERENCES users(user_id) ON DELETE CASCADE;

-------------------------------------------------------------------------------------------------------------
##### For Accounting Entries Migration
CREATE TABLE accounting_entries_backup AS SELECT * FROM accounting_entries;

ALTER TABLE accounting_entries DROP FOREIGN KEY ; -- txn_by
ALTER TABLE accounting_entries DROP FOREIGN KEY ; -- paid_by
ALTER TABLE accounting_entries DROP FOREIGN KEY ; -- received_by



-- Update paid_by
UPDATE accounting_entries ae
JOIN customer_user_mapping m ON ae.paid_by = m.old_customer_id
SET ae.paid_by = m.new_user_id;

-- Update txn_by
UPDATE accounting_entries ae
JOIN customer_user_mapping m ON ae.txn_by = m.old_customer_id
SET ae.txn_by = m.new_user_id;

-- Update received_by
UPDATE accounting_entries ae
JOIN customer_user_mapping m ON ae.received_by = m.old_customer_id
SET ae.received_by = m.new_user_id;




ALTER TABLE accounting_entries
    ADD CONSTRAINT fk_acc_entries_paid_by FOREIGN KEY (paid_by) REFERENCES users(user_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_acc_entries_txn_by FOREIGN KEY (txn_by) REFERENCES users(user_id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_acc_entries_received_by FOREIGN KEY (received_by) REFERENCES users(user_id) ON DELETE CASCADE;



####################################

DROP TABLE customers;
DROP TABLE customer_user_mapping;

