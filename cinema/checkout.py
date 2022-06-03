import json
from dataclasses import asdict
from functools import wraps
from typing import List

from flask import (
    Blueprint, render_template, session, request, url_for, current_app
)
from werkzeug.utils import redirect

from configuration import config
from database_adapter import adapter
from models import Booking, Ticket, Showing, Seat, Movie, PaymentCard

bp = Blueprint('checkout', __name__, url_prefix='/checkout')


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            user = adapter.select_user(session['user_email'])
            return func(*args, **kwargs) if user else redirect(url_for('user.login'))
        except KeyError:
            # user needs to log in

            return redirect(url_for('user.login'))

    return wrapper


def checking_out_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('checking_out'):
            return "Not Found", 404
        return func(*args, **kwargs)

    return wrapper


@bp.route('/', methods=('GET', 'POST'))
@login_required
def checkout():
    session['in_progress'] = True
    adult_price, booking, booking_fee, child_price, movie, num_adult, num_child, \
    num_senior, sales_tax, seats, senior_price, showing, total_price, tickets = _get_booking_info()

    current_app.logger.debug((adult_price, booking, booking_fee, child_price, movie, num_adult, num_child, \
                              num_senior, sales_tax, seats, senior_price, showing, total_price, tickets))
    if request.method == 'POST':
        pass
    return render_template('checkout/checkout.html', num_adult=num_adult, num_child=num_child, num_senior=num_senior,
                           seats=seats, movie=movie, adult_price=adult_price, child_price=child_price,
                           senior_price=senior_price, total_price=total_price, booking_date=showing.datetime,
                           showroom=showing.showRoomID, booking=booking, show_id=showing.showID, sales_tax=sales_tax,
                           booking_fee=booking_fee)


@bp.route('/payment', methods=('GET', 'POST'))
@login_required
def payment():
    session['in_progress'] = True
    session['checking_out'] = True
    adult_price, booking, booking_fee, child_price, movie, num_adult, num_child, \
    num_senior, sales_tax, seats, senior_price, showing, total_price, tickets = _get_booking_info()
    cards = adapter.get_paymentcards(adapter.select_user(session['user_email']).userID)
    for card in cards:
        card['cardNumber'] = str(card['cardNumber'])[-4:]
    if request.method == 'POST':
        session['confirm_info'] = {'total': session.get('total_price'), 'booking_num': booking.bookingID}
        session['checking_out'] = False
        error_message = None
        discount = None
        promo_code = request.form.get('promo_code')
        card_num = request.form.get('card_num')

        if promo_code != "":
            # user is applying promotion
            return _apply_promotion(adult_price, booking, booking_fee, child_price, discount, error_message, movie,
                                    num_adult, num_child, num_senior, promo_code, sales_tax, seats, senior_price,
                                    showing, total_price)
        if request.form.get('submit_button') == 'promo':
            # user hit promo button when field is empty
            payment_cards = adapter.get_paymentcards(adapter.select_user(session['user_email']).userID)
            cards = [PaymentCard(**card) for card in payment_cards]
            for card in cards:
                card.cardNumber = str(card.cardType)[-4:]
            for card in cards:
                card.expirationYear = card.expirationYear + 2020
            return render_template('checkout/payment.html',
                                   cards=[asdict(card) for card in cards],
                                   num_adult=num_adult, num_child=num_child, num_senior=num_senior,
                                   seats=seats, movie=movie, adult_price=adult_price, child_price=child_price,
                                   senior_price=senior_price, total_price=total_price,
                                   booking_date=showing.datetime,
                                   showroom=showing.showRoomID, booking=booking, show_id=showing.showID,
                                   sales_tax=sales_tax,
                                   booking_fee=booking_fee, error_message="Promotion field empty.", discount=discount)
        if card_num is not None:
            # user is submitting payment
            current_app.logger.debug("CARD NUM " + json.dumps(card_num))
            _complete_order(booking, card_num, tickets, total_price)
        else:
            payment_cards = adapter.get_paymentcards(adapter.select_user(session['user_email']).userID)
            cards = [PaymentCard(**card) for card in payment_cards]
            for card in cards:
                card.cardNumber = str(card.cardNumber)[-4:]
            for card in cards:
                card.expirationYear = card.expirationYear + 2020
            session['confirm_info'] = {'total': session.get('total_price'), 'booking_num': booking.bookingID}
            return render_template('checkout/payment.html',
                                   cards=[asdict(card) for card in cards],
                                   num_adult=num_adult, num_child=num_child, num_senior=num_senior,
                                   seats=seats, movie=movie, adult_price=adult_price, child_price=child_price,
                                   senior_price=senior_price, total_price=total_price,
                                   booking_date=showing.datetime,
                                   showroom=showing.showRoomID, booking=booking, show_id=showing.showID,
                                   sales_tax=sales_tax,
                                   booking_fee=booking_fee, error_message="Please provide payment.", discount=discount)
        session['confirm_info'] = {'total': session.get('total_price'), 'booking_num': booking.bookingID}
        return redirect(url_for('email.send_booking_confirmation', user_email=session['user_email']))
    payment_cards = adapter.get_paymentcards(adapter.select_user(session['user_email']).userID)
    cards = [PaymentCard(**card) for card in payment_cards]
    for card in cards:
        card.expirationYear = card.expirationYear + 2020
    for card in cards:
        card.cardNumber = str(card.cardNumber)[-4:]
    return render_template('checkout/payment.html',
                           cards=[asdict(card) for card in cards],
                           num_adult=num_adult, num_child=num_child, num_senior=num_senior,
                           seats=seats, movie=movie, adult_price=adult_price, child_price=child_price,
                           senior_price=senior_price, total_price=total_price, booking_date=showing.datetime,
                           showroom=showing.showRoomID, booking=booking, show_id=showing.showID,
                           sales_tax=sales_tax,
                           booking_fee=booking_fee)


def _apply_promotion(adult_price, booking, booking_fee, child_price, discount, error_message, movie, num_adult,
                     num_child, num_senior, promo_code, sales_tax, seats, senior_price, showing, total_price):
    current_app.logger.info(f"{session.get('user_email')} is applying a promo code.")
    promotions = adapter.get_promotions()
    try:
        promo = [promo for promo in promotions if promo['code'] == promo_code].pop()
        discount = (total_price * float(promo['discount'] / 100))
        total_price -= discount
        current_app.logger.debug((promo['discount'], discount, total_price))
        booking.totalPrice = total_price
        session['total_price'] = booking.totalPrice
        booking.promoID = promo['promoID']
        session['booking']['booking'] = booking
        current_app.logger.info("Valid promo code.")
        session['promo'] = total_price
    except IndexError:
        # user has entered incorrect promo code
        current_app.logger.info("Invalid promo code.")
        error_message = "Invalid Promotion Code"
    return render_template('checkout/payment.html',
                           cards=adapter.get_paymentcards(
                               adapter.select_user(session['user_email']).userID),
                           num_adult=num_adult, num_child=num_child, num_senior=num_senior,
                           seats=seats, movie=movie, adult_price=adult_price, child_price=child_price,
                           senior_price=senior_price, total_price=total_price,
                           booking_date=showing.datetime,
                           showroom=showing.showRoomID, booking=booking, show_id=showing.showID,
                           sales_tax=sales_tax,
                           booking_fee=booking_fee, error_message=error_message, discount=discount)


def _complete_order(booking, card_num, tickets, total_price):
    current_app.logger.debug(json.dumps(card_num))
    card = PaymentCard(**json.loads(card_num.replace("'", '"')))
    current_app.logger.info(
        f"{session.get('user_email')} is completing the purchase with paymentcard {card.cardType}")
    booking.paymentID = card.paymentID
    booking.totalPrice = total_price if not session.get('total_price') else session.get('total_price')
    if session.get('promo'):
        booking.totalPrice = session.get('promo')
    # insert booking into database
    booking.promoID = None if booking.promoID < 0 else booking.promoID
    booking.bookingID = adapter.insert_booking(booking)
    seats: List[Seat] = [Seat(**seat) for seat in session['booking']['seats']]
    current_app.logger.info(f"Inserted booking {booking.bookingID} into database.")
    for ticket in tickets:
        # insert tickets into database
        ticket.bookingID = booking.bookingID
        ticket.ticketID = adapter.insert_ticket(ticket)
        current_app.logger.info(f"Inserted ticket {ticket.ticketID} into database.")
        for seat in seats:
            if seat.seatID == ticket.seatID:
                # assign this seat to the inserted ticket in the database
                adapter.set_seat_taken(seat.seatID, ticket.ticketID)
                current_app.logger.info(
                    f"Seat {seat.seatID} set taken by ticket {ticket.ticketID} in database.")


def _get_booking_info():
    booking: Booking = Booking(**session['booking']['booking'])
    seats: List[Seat] = [Seat(**seat) for seat in session['booking']['seats']]
    showing: Showing = adapter.get_showing(booking.showingID)
    movie: Movie = adapter.get_movie(showing.movieID)
    adult_type_id = adapter.get_adult_type().ticketTypeID
    child_type_id = adapter.get_child_type().ticketTypeID
    senior_type_id = adapter.get_senior_type().ticketTypeID
    tickets: List[Ticket] = [Ticket(**ticket) for ticket in session['booking']['tickets']]
    num_adult = len([ticket for ticket in tickets if ticket.typeID == adult_type_id])
    num_child = len([ticket for ticket in tickets if ticket.typeID == child_type_id])
    num_senior = len([ticket for ticket in tickets if ticket.typeID == senior_type_id])
    adult_price = num_adult * adapter.get_adult_type().price
    child_price = num_child * adapter.get_child_type().price
    senior_price = num_senior * adapter.get_senior_type().price
    total_ticket_price = adult_price + child_price + senior_price
    booking_fee = adapter.get_booking_fee()['price']
    total_price = total_ticket_price + booking_fee
    sales_tax = config['sales_tax'] * total_price
    total_price += sales_tax
    seats: List[str] = [f"{seat.rowLetter}{seat.seatNum}" for seat in seats]
    seats: str = ",".join(seats)
    return adult_price, booking, booking_fee, child_price, movie, num_adult, num_child, num_senior, sales_tax, seats, senior_price, showing, total_price, tickets
