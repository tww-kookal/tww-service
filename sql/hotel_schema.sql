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
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE SET NULL
);

-- Create Rooms Table
CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    room_type VARCHAR(50),
    price_per_night DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

-- Create Bookings Table
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

-- Sample Roles
INSERT INTO roles (role_name) VALUES ('admin'), ('manager'), ('guest');

-- Sample Rooms
INSERT INTO rooms (room_name, room_type, price_per_night) VALUES
('Room 101', 'Single', 50.00),
('Room 102', 'Double', 80.00),
('Room 201', 'Suite', 120.00);

-- Pre-seeded Admin User
-- Password: Admin@123
INSERT INTO users (username, password, role_id)
VALUES ('admin', '$2b$12$RrR2rIF6nDZo1h5pV2n5dOZc7rfkq8Y2nZtB5T9e.XjT1u0mYpp9K', 1);

commit;

update users set password = '$2b$12$XExvNU1rbLFF0dsXmzoJb.JZCkx4S2hQt7TR3vcfM/5kJ4MqQicwi' where username = "admin";