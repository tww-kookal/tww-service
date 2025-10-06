from ..data import bookingDB
from . import roomsHelper as roomHelper
from . import usersHelper as userHelper
from . import customersHelper as customerHelper
from . import paymentsHelper as paymentHelper
from .BizExceptions import CustomerNotAvailableException, RoomNotAvailableException, BookingNotFoundException
import traceback
import logging
from datetime import date

####### Logger ############
logger = logging.getLogger("tww.service.bookingHelper")

def getAvailableRooms(check_in, check_out, number_of_people, room_id):
    try:
        available_rooms = bookingDB.queryAvailableRoomsDB(check_in, check_out, number_of_people, room_id)
        return available_rooms
    except Exception as e:
        logger.error(f"Exception in getAvailableRooms: {e}")
        traceback.print_exc()
        return []

def getCustomerByID(customer_id: str):
    customer = customerHelper.getCustomerByID(customer_id)
    if not customer:
        logger.error(f"Customer not found")
        raise CustomerNotAvailableException()
    return customer

def none_if_zero(value):
    return None if value == 0 or value == '' else value
    
def bookRoom(booking: dict, is_update=False):
    logger.debug(f"Received Booking: {booking}")

    bookingUser = userHelper.getUserByUserName(booking["booked_by"], throw_exception=True)
    booking["source_of_booking_id"] = none_if_zero(booking["source_of_booking_id"])
    booking["booked_by_id"] = bookingUser["user_id"]

    logger.debug(f"Persisting Booking Room: {booking}, {is_update}")
    if(is_update):
        old_booking = bookingDB.getBookingById(booking["booking_id"])
        is_same_booking = old_booking["room_id"] == booking["room_id"] and (old_booking["check_in"] == booking["check_in"] or old_booking["check_out"] == booking["check_out"])
        logger.debug(f"Same Booking: {is_same_booking}")
        if not is_same_booking:
            #Check for room availability
            #Check if the selected room is available
            selectedRoom = getSelectedRoom(booking["check_in"], booking["check_out"], booking["number_of_people"], booking["room_id"])
            logger.debug(f"Selected Room: {selectedRoom}")
            if not selectedRoom:
                logger.error(f"Selected Room not available")
                raise RoomNotAvailableException("Selected Room not available for the dates")            
        bookedRoom = bookingDB.updateBookingDB(booking)
        logger.debug(f"Updated Booking: {bookedRoom}")
    else:
        selectedRoom = getSelectedRoom(booking["check_in"], booking["check_out"], booking["number_of_people"], booking["room_id"])
        if not selectedRoom:
            logger.error(f"Selected Room not available")
            raise RoomNotAvailableException("Selected Room not available for the dates")
        bookedRoom = bookingDB.persistBookingDB(booking)

    # Add Names to the return object for display
    bookedRoom["booked_by"] = userHelper.getFullNameOfUserByID(bookedRoom["booked_by_id"])
    customer = getCustomerByID(bookedRoom["customer_id"])
    bookedRoom["customer_name"] = customer["customer_name"]
    bookedRoom["customer_phone"] = customer["phone"]
    bookedRoom['room_name'] = roomHelper.getRoomById(bookedRoom['room_id'])['room_name']
    return bookedRoom

def search_bookings(search_criteria: dict):
    try:
        return bookingDB.search_bookings(search_criteria)
    except Exception as e:
        logger.error(f"Exception in search_bookings: {e}")
        traceback.print_exc()
        return []

def listBookingsSince(startingDate: date = date(2020, 1, 1), is_check_in_date = False):
    try:
        return bookingDB.listBookingsSinceDB(startingDate, is_check_in_date)
    except Exception as e:
        logger.error(f"Exception in listAllBookings: {e}")
        traceback.print_exc()
        return []

def guestsForDay(forDate: date):
    try:
        return bookingDB.guestsForDay(forDate=forDate)[0]
    except Exception as e:
        logger.error(f"Exception in no_of_guest: {e}")
        traceback.print_exc()
        raise Exception("Not able to get the number of guests")

def getSelectedRoom(check_in: date, check_out: date, number_of_peope: int, room_id: int):
    availableRooms = bookingDB.queryAvailableRoomsDB(
        check_in, check_out, number_of_peope, room_id
    )
    if not availableRooms or len(availableRooms) == 0:
        logger.error(f"No available rooms for the given date range")
        raise RoomNotAvailableException()
    
    if availableRooms and len(availableRooms) == 1:
        return availableRooms[0]
    else:
        logger.info(f"Selected Room not available")
        raise RoomNotAvailableException("Selected Room not available")

def getBookingByID(booking_id: int):
    booking = bookingDB.getBookingById(booking_id)
    if not booking:
        logger.error(f"Booking not found for id {booking_id}")
        raise BookingNotFoundException(f"Booking not found for id {booking_id}")
    #Get the Payment Details for this booking
    booking["payments"] = paymentHelper.getPaymentsForBooking(booking_id)
    return booking