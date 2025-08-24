###python -m app.backend.csvToBooking

import csv
import os
from datetime import datetime
from app.backend import bookingDB, customersDB, usersDB, paymentDB, database

conn = database.get_connection()
backend_user_id = int(os.getenv("BATCH_JOB_ID"))
file_name = (os.getenv("FILE_NAME"))
print(f"Batch Job : {backend_user_id} {file_name}")

def makePayments(booking) :
    if booking["advance_payment"] or 0 > 0:
        payment = {
            "booking_id": booking["booking_id"],
            "payment_type": 'gpay',
            "payment_amount": booking["advance_payment"] or 0,
            "payment_date": booking["booking_date"],
            "payment_to": booking["advance_paid_to"] or backend_user_id,
            "payment_for": 'advance',
            "payment_added_by": backend_user_id,
            "remarks": 'MIGRATED'
        }
        paymentDB.persistPaymentDB(payment, conn)

    if  booking["balance_to_pay"] or 0 > 0:
        payment = {
            "booking_id": booking["booking_id"],
            "payment_type": 'gpay',
            "payment_amount": booking["balance_to_pay"],
            "payment_date": booking["check_out"],
            "payment_to": booking["balance_paid_to"] or backend_user_id,
            "payment_for": 'balance',
            "payment_added_by": backend_user_id,
            "remarks": 'MIGRATED'
        }
        paymentDB.persistPaymentDB(payment, conn)


def load_csv_and_insert_bookings(csv_filename= file_name):
    input_path = os.path.join(os.path.dirname(__file__), csv_filename)
    failure_rows = []

    with open(input_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            over_all_status = "Success"
            customer_status = "FAILED"
            source_of_booking_status = "FAILED"
            advance_paid_to_status = "FAILED"
            balance_paid_to_status = "FAILED"
            try:                
                # Check or insert customer
                customer_name = row.get("customer_name")
                phone = row.get("phone")
                customer = None
                print()
                print(f"Customer {customer_name}", end = ":: ")
                if customer_name :
                    existing_customers = customersDB.queryCustomerByNameAndPhoneDB(customer_name, phone, conn)
                    if existing_customers:
                        customer = existing_customers[0]
                        print(f"found :: ", end="")
                    else:
                        new_customer = {
                            "customer_name": customer_name,
                            "email": row.get("email") or "NO_EMAIL",
                            "phone": phone or "NO_PHONE",
                            "area": row.get("area") or "NO_AREA",
                            "city": row.get("city") or "NO_CITY",
                            "state": row.get("state") or "NO_STATE",
                            "country": row.get("country") or "NO_COUNTRY",
                            "zip_code": row.get("zip_code") or "NO_ZIP",
                        }
                        print(f"create :: ", end="")
                        customer = customersDB.createCustomerDB(new_customer, conn)
                if customer:
                    customer_status = "PASSED"

                # Check or insert source_of_booking user
                source_username = row.get("source_of_booking") or ''
                source_user = None
                commission_percent = 0
                if source_username:
                    source_user = usersDB.queryUserDB(source_username.lower(), conn)
                    commission_percent = source_user["booking_commission"] if source_user else 0

                if source_user:
                    source_of_booking_status = "PASSED"

                advance_paid_to = row.get("advance_paid_to") or ''
                advance_paid_to_user = {"user_id": None}

                if advance_paid_to is None or advance_paid_to == '':
                    advance_paid_to_user = {"user_id": None}
                else: 
                    x = usersDB.queryUserDB(advance_paid_to.lower(), conn)

                    advance_paid_to_user = x or {"user_id": None}

                # Fetch Balance Paid To user
                balance_paid_to = row.get("balance_paid_to") or ''
                balance_paid_user = {"user_id": None}
                if balance_paid_to is None or balance_paid_to == '':
                    balance_paid_user = {"user_id": None}
                else: 
                    x = usersDB.queryUserDB(balance_paid_to.lower(), conn)

                    balance_paid_user = x or {"user_id": None}

                print(f"Source", end = " : ")
                print(f"{source_user['username']}", end = " :: ")
                # Fetch Advance Paid To user

                check_in = datetime.strptime(row.get("check_in"), "%Y-%m-%d").date() if row.get("check_in") else None
                booking_date = datetime.strptime(row.get("booking_date"), "%Y-%m-%d").date() if row.get("booking_date") else check_in
                               
                int(row.get("room_id") or 0),
                int(row.get("number_of_people") or 0),
                float(row.get("room_price") or 0),
                float(row.get("advance_payment") or 0),
                float(row.get("total_price") or 0),
                float(row.get("commission") or 0),
                float(row.get("balance_to_pay") or 0),
                print(f"SET :::", end="")
                # Prepare booking dict
                booking = {
                    "customer_id": customer["customer_id"],
                    "room_id": int(row.get("room_id") or 0),
                    "number_of_people": int(row.get("number_of_people") or 0),
                    "check_in": check_in,
                    "check_out": datetime.strptime(row.get("check_out"), "%Y-%m-%d").date() if row.get("check_out") else None,
                    "status": row.get("status") or "confirmed",
                    "booking_date": booking_date,
                    "booked_by_id": backend_user_id, #BATCH_JOB_USER
                    "source_of_booking_id": source_user["user_id"],
                    "room_price": float(row.get("room_price") or 0),
                    "advance_payment": float(row.get("advance_payment") or 0),
                    "advance_paid_to": advance_paid_to_user["user_id"] or None,
                    "advance_payment_method": 'GPAY',
                    "food_price": float(row.get("food_price") or 0),
                    "service_price": float(row.get("service_price") or 0),
                    "tax_percent": 0,
                    "tax_price": 0,
                    "discount_price": 0,
                    "total_price": float(row.get("total_price") or 0),
                    "final_price_paid_to": balance_paid_user["user_id"] or None,
                    "is_final_price_paid": (row.get("is_final_price_paid") or "0").lower() == 1,
                    "final_price_payment_method": 'GPAY',
                    "commission": float(row.get("commission") or 0),
                    "commission_percent": commission_percent or 0,
                    "is_commission_settled": (row.get("is_commission_settled") or "0").lower() == 1,
                    "remarks": row.get("remarks") or "",
                    "balance_to_pay": float(row.get("balance_to_pay") or 0),
                    "is_balance_paid": (row.get("is_balance_paid") or "0").lower() == 1,
                    "balance_paid_to": balance_paid_user["user_id"] or None,
                    "balance_payment_method": 'GPAY',
                }
                print(f"Cond:: {source_of_booking_status == 'FAILED' or customer_status == 'FAILED'}", end = ": ")
                if source_of_booking_status == 'FAILED' or customer_status == 'FAILED':
                    over_all_status = "FAILED"
                    failure_rows.append({**row, "customer_status": customer_status, "source_of_booking_status": source_of_booking_status, "advance_paid_to_status": advance_paid_to_status, "balance_paid_to_status": balance_paid_to_status, "over_all_status": over_all_status})
                    continue

                print(f"Booking Object ::: {booking["room_id"]}", end = "")
                createdBooking = bookingDB.persistBookingDB(booking, conn)

                booking["booking_id"] = createdBooking["booking_id"]
                print(f"Booking ID ::::::: {booking["booking_id"]}", end = "")
                makePayments(booking)
                conn.commit()
            except Exception as e:
                print(f":::Exception ::: {e}")
                over_all_status = "FAILED"
                failure_rows.append({**row, "customer_status": customer_status, "source_of_booking_status": source_of_booking_status, "advance_paid_to_status": advance_paid_to_status, "balance_paid_to_status": balance_paid_to_status, "over_all_status": over_all_status})

    # Write failures to separate CSV
    if failure_rows:
        failure_csv_path = os.path.join(os.path.dirname(__file__), "booking_failures.csv")
        with open(failure_csv_path, mode='w', newline='', encoding='utf-8') as failure_csvfile:
            fieldnames = list(failure_rows[0].keys())
            writer = csv.DictWriter(failure_csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for fail_row in failure_rows:
                writer.writerow(fail_row)

    return len(failure_rows)

if __name__ == "__main__":
    print("CSV to Booking Script Started")
    failure_count = load_csv_and_insert_bookings()
    print(f"CSV to Booking Script Finished with {failure_count} failures")
