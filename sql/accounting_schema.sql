

CREATE TABLE accounting_categories (
    acc_category_id INT PRIMARY KEY AUTO_INCREMENT,
    acc_category_name VARCHAR(100) NOT NULL,
    acc_category_type ENUM('debit', 'credit') NOT NULL
);

CREATE TABLE accounting_entries (
    acc_entry_id INT PRIMARY KEY AUTO_INCREMENT,
    acc_category_id INT NOT NULL,
    acc_entry_amount DECIMAL(10,2) NOT NULL,
    acc_entry_description TEXT,
    acc_entry_date DATE NOT NULL,
    created_by INT NOT NULL,
    txn_by INT NOT NULL,
    paid_by INT NOT NULL,
    received_by INT NOT NULL,
    received_for_booking_id INT,
    payment_type ENUM('gpay', 'cash', 'bank', 'upi', 'cc', 'dc') NOT NULL DEFAULT 'gpay',
    FOREIGN KEY (acc_category_id) REFERENCES accounting_categories(acc_category_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (paid_by) REFERENCES customers(customer_id),
    FOREIGN KEY (txn_by) REFERENCES customers(customer_id),
    FOREIGN KEY (received_by) REFERENCES customers(customer_id),
    FOREIGN KEY (received_for_booking_id) REFERENCES bookings(booking_id)
);

INSERT INTO accounting_categories (acc_category_id, acc_category_name, acc_category_type) VALUES
    (1, 'Grocery Purchase', 'debit'),
    (2, 'Amenities Purchase', 'debit'),
    (3, 'Food Purchase', 'debit'),
    (4, 'Vegetables Purchase', 'debit'),
    (5, 'Meat/Egg/Fish Purchase', 'debit'),
    (6, 'Salary Payments', 'debit'),
    (7, 'Salary Advance Payments', 'debit'),
    (8, 'Guest Paid', 'credit'),
    (9, 'Refund to Guest', 'debit'),
    (10, 'Maintenance Cost', 'debit')
    (11, 'Advance Payment', 'credit'),
    (12, 'Part Payment', 'credit'),
    (13, 'Balance Payment', 'credit'),
    (14, 'Refund from Vendor', 'credit'),
    (15, 'Commission Payout', 'debit'),
    (16, 'Food Bill for Guest', 'credit');

INSERT INTO accounting_categories (acc_category_name, acc_category_type) VALUES
('Food Bill for Guest', 'credit');

INSERT INTO accounting_entries 
(acc_category_id, acc_entry_amount, acc_entry_description, acc_entry_date, created_by, txn_by, paid_by, received_by, received_for_booking_id, payment_type)
select case payment_for when 'advance' then 11 when 'balance' then 13 when 'part-pay' then 12 end as acc_category_id,
	payment_amount as acc_entry_amount, bp.remarks as acc_entry_description, payment_date as acc_entry_date, payment_added_by as created_by,
    272  as txn_by, c.customer_id, 272 as received_by, b.booking_id as received_for_booking_id, payment_type
from booking_payments bp 
inner join bookings b on (b.booking_id = bp.booking_id) 
inner join customers  c  on (c.customer_id = b.customer_id) ;
