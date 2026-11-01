import pytest
from unittest.mock import patch
from app.biz import paymentsHelper
from app.biz.BizExceptions import BookingNotFoundException, PaymentExceededException

# getPaymentsForBooking
@patch('app.biz.paymentsHelper.paymentDB.queryPaymentsForBooking')
def test_getPaymentsForBooking_found(mock_query):
    mock_query.return_value = ['payment1']
    assert paymentsHelper.getPaymentsForBooking(1) == ['payment1']

@patch('app.biz.paymentsHelper.paymentDB.queryPaymentsForBooking')
def test_getPaymentsForBooking_none(mock_query):
    mock_query.return_value = []
    assert paymentsHelper.getPaymentsForBooking(1) == []

# getTotalBookingPrice
@patch('app.biz.paymentsHelper.bookingHelper.getBookingByID')
def test_getTotalBookingPrice_found(mock_get):
    mock_get.return_value = {'total_price': 100}
    assert paymentsHelper.getTotalBookingPrice(1) == 100

@patch('app.biz.paymentsHelper.bookingHelper.getBookingByID')
def test_getTotalBookingPrice_zero(mock_get):
    mock_get.return_value = {'total_price': 0}
    assert paymentsHelper.getTotalBookingPrice(1) == 0

@patch('app.biz.paymentsHelper.bookingHelper.getBookingByID')
def test_getTotalBookingPrice_none(mock_get):
    mock_get.return_value = {'total_price': None}
    assert paymentsHelper.getTotalBookingPrice(1) == 0

@patch('app.biz.paymentsHelper.bookingHelper.getBookingByID')
def test_getTotalBookingPrice_not_found(mock_get):
    mock_get.return_value = None
    with pytest.raises(BookingNotFoundException):
        paymentsHelper.getTotalBookingPrice(1)

# deletePayment
@patch('app.biz.paymentsHelper.paymentDB.deletePaymentDB')
def test_deletePayment(mock_delete):
    paymentsHelper.deletePayment(1)
    mock_delete.assert_called_once_with(1)

# addPayment (persist)
@patch('app.biz.paymentsHelper.getPaymentsForBooking')
@patch('app.biz.paymentsHelper.validatePaymentAmount')
@patch('app.biz.paymentsHelper.userHelper.getUserByUserName')
@patch('app.biz.paymentsHelper.paymentDB.persistPaymentDB')
def test_addPayment_persist(mock_persist, mock_user, mock_validate, mock_get):
    mock_get.return_value = []
    mock_validate.return_value = True
    mock_user.return_value = {'user_id': 2}
    mock_persist.return_value = {'payment_id': 1}
    payment = {'booking_id': 1, 'payment_added_by': 'user', 'payment_amount': 50}
    result = paymentsHelper.addPayment(payment)
    assert result == {'payment_id': 1}
    assert payment['payment_added_by'] == 2

# addPayment (update)
@patch('app.biz.paymentsHelper.getPaymentsForBooking')
@patch('app.biz.paymentsHelper.validatePaymentAmount')
@patch('app.biz.paymentsHelper.userHelper.getUserByUserName')
@patch('app.biz.paymentsHelper.paymentDB.updatePaymentDB')
def test_addPayment_update(mock_update, mock_user, mock_validate, mock_get):
    mock_get.return_value = []
    mock_validate.return_value = True
    mock_user.return_value = {'user_id': 2}
    mock_update.return_value = {'payment_id': 1}
    payment = {'booking_id': 1, 'payment_added_by': 'user', 'payment_amount': 50}
    result = paymentsHelper.addPayment(payment, is_update=True)
    assert result == {'payment_id': 1}
    assert payment['payment_added_by'] == 2

# validatePaymentAmount
@patch('app.biz.paymentsHelper.getTotalBookingPrice')
def test_validatePaymentAmount_valid(mock_total):
    mock_total.return_value = 100
    payment = {'booking_id': 1, 'payment_amount': 50, 'payment_for': 'booking'}
    payments = [{'payment_amount': 30, 'payment_for': 'booking'}]
    assert paymentsHelper.validatePaymentAmount(payment, payments) is True

@patch('app.biz.paymentsHelper.getTotalBookingPrice')
def test_validatePaymentAmount_exceeded(mock_total):
    mock_total.return_value = 100
    payment = {'booking_id': 1, 'payment_amount': 80, 'payment_for': 'booking'}
    payments = [{'payment_amount': 30, 'payment_for': 'booking'}]
    with pytest.raises(PaymentExceededException):
        paymentsHelper.validatePaymentAmount(payment, payments)

@patch('app.biz.paymentsHelper.getTotalBookingPrice')
def test_validatePaymentAmount_refund(mock_total):
    mock_total.return_value = 100
    payment = {'booking_id': 1, 'payment_amount': 50, 'payment_for': 'booking'}
    payments = [{'payment_amount': 30, 'payment_for': 'refund'}]
    assert paymentsHelper.validatePaymentAmount(payment, payments) is True