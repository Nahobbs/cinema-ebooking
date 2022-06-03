import datetime
import json
import string
from dataclasses import asdict
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, render_template, current_app, session, url_for
)
from flask import (
    request
)
from werkzeug.utils import redirect

from database_adapter import adapter
from models import Movie, Showing, Booking, Ticket

bp = Blueprint('booking', __name__, url_prefix='/booking')


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


def booking_in_progress_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('booking_ip'):
            return "Not Found", 404
        return func(*args, **kwargs)

    return wrapper


@bp.route('/tickets/<show_id>', methods=('GET', 'POST'))
@login_required
def book_tickets(show_id):
    session['ticket_info'] = None
    session['in_progress'] = True
    showing: Showing = adapter.get_showing(show_id=show_id)
    movie: Movie = adapter.get_movie(movie_id=showing.movieID)
    if request.method == 'POST':
        session['booking_ip'] = True
        num_child_tickets = int(request.form['num_child_tickets'])
        num_adult_tickets = int(request.form['num_adult_tickets'])
        num_senior_tickets = int(request.form['num_senior_tickets'])
        num_tickets = num_adult_tickets + num_child_tickets + num_senior_tickets
        current_app.logger.debug(f"Child Tickets: {num_child_tickets}, Adult Tickets: {num_adult_tickets}")
        if num_adult_tickets == 0 and num_child_tickets == 0 and num_senior_tickets == 0:
            error_message = "You must choose at least one ticket."
            return render_template('booking/book_ticket.html', movie=asdict(movie), error_message=error_message)
        seats_remaining_in_showroom = adapter.get_available_seats_in_showroom(showing.showRoomID)
        current_app.logger.debug(
            f"{len(seats_remaining_in_showroom)} seats remaining in showroom #{showing.showRoomID}")
        if num_tickets > len(seats_remaining_in_showroom):
            error_message = "Not enough seats remaining to satisfy your order."
            return render_template('booking/book_ticket.html', movie=asdict(movie), error_message=error_message,
                                   child=adapter.get_child_type().price,
                                   senior=adapter.get_senior_type().price, adult=adapter.get_adult_type().price,
                                   show_id=show_id)
        session['ticket_info'] = {'num_child_tickets': num_child_tickets, 'num_adult_tickets': num_adult_tickets,
                                  'num_tickets': num_tickets, 'showing': showing,
                                  'num_senior_tickets': num_senior_tickets}
        return redirect(url_for('booking.select_seats'))
    return render_template('booking/book_ticket.html', movie=asdict(movie), child=adapter.get_child_type().price,
                           senior=adapter.get_senior_type().price, adult=adapter.get_adult_type().price)


@bp.route('/select_seats/', methods=('GET', 'POST'))
@booking_in_progress_required
@login_required
def select_seats():
    session['in_progress'] = True
    session['booking'] = None
    booking_details: dict = session.get('ticket_info')
    showing = Showing(**booking_details.get('showing'))
    seats = adapter.get_seats_in_showroom(showing.showRoomID)
    row = list()
    seats = [seat for i in range(1, 9) for seat in seats if seat.seatNum == i]
    [row.append([seat for seat in seats if seat.rowLetter == letter]) for letter in list(string.ascii_uppercase)[0:8]]
    if request.method == 'POST':
        # get AJAX post parameters
        data = request.form['seats']
        jquery_result = json.loads(data)['seats']
        selected_seats = []

        # retrieve selected seats
        [selected_seats.append(
            adapter.get_selected_seats(showing.showRoomID, seat_info['rowLetter'], seat_info['seatNum'])) for seat_info
            in jquery_result]

        seats = selected_seats.copy()
        adult_type = adapter.get_adult_type()
        child_type = adapter.get_child_type()
        senior_type = adapter.get_senior_type()
        # create booking
        booking = Booking(userID=adapter.select_user(session['user_email']).userID,
                          bookingTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                          ,
                          showingID=Showing(**booking_details['showing']).showID, noOfTickets=len(selected_seats))
        # create tickets
        tickets = []
        [tickets.append(Ticket(typeID=child_type.ticketTypeID, seatID=selected_seats.pop().seatID)) for _ in
         range(booking_details.get('num_child_tickets'))]
        [tickets.append(Ticket(typeID=adult_type.ticketTypeID, seatID=selected_seats.pop().seatID)) for _ in
         range(booking_details.get('num_adult_tickets'))]
        [tickets.append(Ticket(typeID=senior_type.ticketTypeID, seatID=selected_seats.pop().seatID)) for _ in
         range(booking_details.get('num_senior_tickets'))]

        # add booking info to the checkout session
        session['booking'] = {'booking': booking, 'tickets': tickets, 'seats': seats}
        session['checking_out'] = True
        return url_for('checkout.checkout')
    return render_template('booking/select_seats.html', num_tickets=booking_details.get('num_tickets'),
                           available_seats=seats, row=row)
