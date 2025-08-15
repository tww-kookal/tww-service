###python -m app.backend.csvToBooking

import csv
import os
from datetime import datetime
from app.backend import bookingDB, customersDB, usersDB

def load_csv_and_insert_bookings(csv_filename="bookings-_2025-07-01_to_2025-07-31_.csv"):
    print(f"Loading CSV file: {csv_filename}")
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
                customer_name = row.get("\ufeffcustomer_name")
                phone = row.get("phone")
                customer = None
                print()
                print(f"Customer {customer_name}", end = ":: ")
                if customer_name :
                    existing_customers = customersDB.queryCustomerByNameAndPhoneDB(customer_name, phone)
                    if existing_customers:
                        customer = existing_customers[0]
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
                        customer = customersDB.createCustomerDB(new_customer)
                if customer:
                    customer_status = "PASSED"

                # Check or insert source_of_booking user
                source_username = row.get("source_of_booking") or ''
                source_user = None
                if source_username:
                    source_user = usersDB.queryUserDB(source_username.lower())

                if source_user:
                    source_of_booking_status = "PASSED"

                print(f"Source {source_username}", end = ":: ")
                # Fetch Advance Paid To user
                advance_paid_to = row.get("advance_paid_to") or ''
                advance_paid_to_user = {"user_id": None}

                if advance_paid_to is None or advance_paid_to == '':
                    advance_paid_to_user = {"user_id": None}
                else: 
                    x = usersDB.queryUserDB(advance_paid_to.lower())
                    advance_paid_to_user = x or {"user_id": None}

                if advance_paid_to_user:
                    advance_paid_to_status = "PASSED"
                print(f"Advance {advance_paid_to}", end = ":: ")

                # Fetch Balance Paid To user
                balance_paid_to = row.get("balance_paid_to") or ''
                balance_paid_user = {"user_id": None}
                if balance_paid_to is None or balance_paid_to == '':
                    balance_paid_user = {"user_id": None}
                else: 
                    x = usersDB.queryUserDB(balance_paid_to.lower())
                    balance_paid_user = x or {"user_id": None}
                if balance_paid_user:
                    balance_paid_to_status = "PASSED"

                check_in = datetime.strptime(row.get("check_in"), "%Y-%m-%d").date() if row.get("check_in") else None
                booking_date = datetime.strptime(row.get("booking_date"), "%Y-%m-%d").date() if row.get("booking_date") else check_in
                
                # Prepare booking dict
                booking = {
                    "customer_id": customer["customer_id"],
                    "room_id": int(row.get("room_id") or 0),
                    "number_of_people": int(row.get("number_of_people")) or 0,
                    "check_in": check_in,
                    "check_out": datetime.strptime(row.get("check_out"), "%Y-%m-%d").date() if row.get("check_out") else None,
                    "status": row.get("status") or "confirmed",
                    "booking_date": booking_date,
                    "booked_by_id": 13, #BATCH_JOB_USER
                    "source_of_booking_id": source_user["user_id"],
                    "room_price": float(row.get("room_price")) or 0,
                    "advance_payment": float(row.get("advance_payment") or 0) or 0,
                    "advance_paid_to": advance_paid_to_user["user_id"] or None,
                    "advance_payment_method": 'GPAY',
                    "food_price": float(row.get("food_price")) or 0,
                    "service_price": float(row.get("service_price")) or 0,
                    "tax_percent": 0,
                    "tax_price": 0,
                    "discount_price": 0,
                    "total_price": float(row.get("total_price")) or 0,
                    "final_price_paid_to": balance_paid_user["user_id"] or None,
                    "is_final_price_paid": (row.get("is_final_price_paid") or "0").lower() == 1,
                    "final_price_payment_method": 'GPAY',
                    "commission": float(row.get("commission")) or 0,
                    "is_commission_settled": (row.get("is_commission_settled") or "0").lower() == 1,
                    "remarks": row.get("remarks") or "",
                    "balance_to_pay": float(row.get("balance_to_pay") or 0) or 0,
                    "is_balance_paid": (row.get("is_balance_paid") or "0").lower() == 1,
                    "balance_paid_to": balance_paid_user["user_id"] or None,
                    "balance_payment_method": 'GPAY',
                }

                if source_of_booking_status == 'FAILED' or advance_paid_to_status == 'FAILED' or balance_paid_to_status == 'FAILED' or customer_status == 'FAILED':
                    over_all_status = "FAILED"
                    failure_rows.append({**row, "customer_status": customer_status, "source_of_booking_status": source_of_booking_status, "advance_paid_to_status": advance_paid_to_status, "balance_paid_to_status": balance_paid_to_status, "over_all_status": over_all_status})
                    continue

                print(f"Booking Object :::::::", end = "")
                bookingDB.persistBookingDB(booking)

            except Exception as e:
                over_all_status = "FAILED"
                failure_rows.append({**row, "customer_status": customer_status, "source_of_booking_status": source_of_booking_status, "over_all_status": over_all_status})

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
