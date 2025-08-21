use tww_database_dev;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- Create Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    booking_commission INT DEFAULT 0
);

-- Create Roles - User Mapping Table
CREATE TABLE user_roles (
    user_role_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    UNIQUE (user_id, role_id)
);

-- Create Rooms Table
CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    min_capacity INT NOT NULL,
    max_capacity INT NOT NULL,
    number_of_beds INT NOT NULL,
    number_of_bathrooms INT NOT NULL
);

-- Create Customers Table
CREATE TABLE customers (    
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    area VARCHAR(255) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL
);

-- Create Bookings Table
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    room_id INT NOT NULL,
    number_of_people INT NOT NULL DEFAULT 3,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status ENUM('confirmed', 'cancelled', 'checked_in', 'checked_out') NOT NULL DEFAULT 'confirmed',
    booking_date DATE DEFAULT (CURDATE()),
    booked_by_id INT NOT NULL,
    source_of_booking_id INT,
    room_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,

    food_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    service_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_percent DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    discount_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,

    commission_percent DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    commission DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    is_commission_settled BOOLEAN NOT NULL DEFAULT FALSE,
    remarks TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (booked_by_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (source_of_booking_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE booking_payments
(
    booking_payments_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,    
    payment_type ENUM('gpay', 'cash', 'bank', 'upi', 'cc', 'dc') NOT NULL DEFAULT 'gpay',
    payment_amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL DEFAULT (CURDATE()),
    payment_to INT NOT NULL, 
    payment_for ENUM('advance', 'part-pay', 'balance', 'refund') NOT NULL DEFAULT 'advance',
    payment_added_by INT NOT NULL,
    remarks TEXT,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (payment_to) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (payment_added_by) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Sample Roles
INSERT INTO roles (role_name) VALUES ('admin'), ('manager'), ('owner'), ('agent'), ('employee'), ('user');

-- Sample Rooms
INSERT INTO rooms (room_name, min_capacity, max_capacity, number_of_beds, number_of_bathrooms) VALUES
('Cedar', 4, 8, 3, 1),
('Pine', 4, 5, 2, 1),
('Teak', 2, 3, 1, 1),
('Maple', 2, 3, 1, 1),
('Tent', 2, 2, 2, 1),

-- Pre-seeded Admin User
-- Password: adMin@123
INSERT INTO users (username, password, first_name, last_name, email, phone)
VALUES ('admin', '$2b$12$RrR2rIF6nDZo1h5pV2n5dOZc7rfkq8Y2nZtB5T9e.XjT1u0mYpp9K', 'Admin', 'User', 'thewestwood.kookal@gmail.com', '9884855014'); 

-- Pre-seeded all Roles for the Admin User
INSERT INTO user_roles (user_id, role_id)
VALUES (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6);

commit;