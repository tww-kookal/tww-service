###python -m app.backend.csvToBooking

import csv
import os
from datetime import datetime
from app.backend import bookingDB, customersDB, usersDB, paymentDB, database

conn = database.get_connection()
backend_user_id = int(os.getenv("BATCH_JOB_ID"))
file_name = (os.getenv("MMT_FILE_NAME"))
SANGEETHA_USER_ID = int(os.getenv("SANGEETHA_USER_ID"))
print(f"Batch Job : {backend_user_id} {file_name}")

def makePayments(booking) :
        payment = {
            "booking_id": booking["booking_id"],
            "payment_type": 'bank',
            "payment_amount": booking["balance_to_pay"],
            "payment_date": booking["payment_date"],
            "payment_to": booking["balance_paid_to"] or backend_user_id,
            "payment_for": 'balance',
            "payment_added_by": backend_user_id,
            "remarks": 'MIGRATED-MMT'
        }
        paymentDB.persistPaymentDB(payment, conn)


def load_csv_and_insert_bookings(csv_filename= file_name):
    input_path = os.path.join(os.path.dirname(__file__), csv_filename)
    failure_rows = []

    with open(input_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            customer_status = "FAILED"
            try:                
                # Check or insert customer
                customer_name = row.get("customer_name")
                phone = "NO-PHONE"
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

                print(f"Source {source_user['username']}", end = " : ")
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
                    "food_price": float(row.get("food_price") or 0),
                    "service_price": float(row.get("service_price") or 0),
                    "tax_percent": 0,
                    "tax_price": 0,
                    "discount_price": 0,
                    "total_price": float(row.get("room_price") or 0),
                    "balance_to_pay": float(row.get("balance_payment") or 0),
                    "balance_paid_to": SANGEETHA_USER_ID,
                    "final_price_payment_method": 'bank',
                    "commission": float(row.get("commission") or 0),
                    "is_commission_settled": 1,
                    "payment_date": datetime.strptime(row.get("payment_date"), "%Y-%m-%d").date() if row.get("payment_date") else None,
                    "commission_percent": commission_percent or 0,
                    "remarks": row.get("remarks") or ""
                }
                print(f"Cond:: {source_of_booking_status == 'FAILED' or customer_status == 'FAILED'}", end = ": ")
                if source_of_booking_status == 'FAILED' or customer_status == 'FAILED':
                    over_all_status = "FAILED"
                    failure_rows.append({**row, "customer_status": customer_status, "source_of_booking_status": source_of_booking_status, "over_all_status": over_all_status})
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
