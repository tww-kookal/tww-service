web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

mariadb --only-binary=:all:1.1.13

TWILIO - API - 
  ZMDJ9ML41QBGZPVZKXRMD6S1
  +14155238886
  key-load

#################MYSQL###################
SELECT r.room_name, min_capacity, max_capacity
FROM rooms r
LEFT JOIN bookings b 
    ON r.room_id = b.room_id
    AND (
        b.check_in < '2025-06-10' AND b.check_out > '2025-06-04'
    )
WHERE b.booking_id IS NULL
  AND 3 BETWEEN r.min_capacity AND r.max_capacity;
#########################################
