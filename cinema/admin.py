from dataclasses import asdict
from datetime import datetime, timedelta
from functools import wraps

from flask import (Blueprint, render_template, session, url_for, request, current_app)
from werkzeug.utils import redirect

from cinema.email import send_email
from cinema.user import _encrypt_password
from database_adapter import adapter
from models import Movie, Address, User

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            user = adapter.select_user(session['user_email'])
            return func(*args, **kwargs) if user.isAdmin else redirect(url_for('user.login'))
        except (KeyError, AttributeError):
            # user needs to log in
            return redirect(url_for('user.login'))

    return wrapper


@bp.route('/view', methods=('GET', 'POST'))
@admin_required
def view():
    return render_template('admin/admin-view.html', admin_name=adapter.select_admin(session['user_email']).firstName)


@bp.route('/members/', methods=('GET', 'POST'))
@admin_required
def manage_members():
    states = {'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona',
              'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware',
              'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho',
              'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
              'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
              'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi', 'MT': 'Montana',
              'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire',
              'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma',
              'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina',
              'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia',
              'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia',
              'WY': 'Wyoming'}
    if request.method == 'POST':
        action = request.form['action']
        if action == 'edit':
            if request.form['user_select'] == 'add':
                return render_template('admin/manage-members.html',
                                       users=[asdict(user) for user in adapter.select_all_users()], edit_user=False,
                                       add_user=True, user=None, states=states, user_address=None)
            else:
                user = adapter.select_user(request.form['user_select'])
                return render_template('admin/manage-members.html',
                                       users=[asdict(user) for user in adapter.select_all_users()], edit_user=True,
                                       add_user=False, user=asdict(user), states=states,
                                       user_address=adapter.select_address(user.shippingAddressID))
        elif action == 'unsuspend':
            if request.form['user_select'] == 'add':
                # todo error message
                pass
            else:
                adapter.unsuspend_user(adapter.select_user(request.form['user_select']).userID)
        elif action == 'suspend':
            if request.form['user_select'] == 'add':
                # todo error message
                pass
            else:
                adapter.suspend_user(adapter.select_user(request.form['user_select']).userID)
        elif action == 'update_user' or action == 'add_admin' or action == 'add_user':
            if action == 'update_user': user = adapter.select_user_by_id(request.form['user_id'])
            else:
                user = User(firstName='', lastName='', email='', email_confirmed=False, password='', phone='',
                            promotions=False, isAdmin=False, isSuspended=False)
            try:
                request.form['email_confirmed'] == 'on'
                user.email_confirmed = 1
            except KeyError:
                user.email_confirmed = 0
            try:
                request.form['promotions'] == 'on'
                user.promotions = 1
            except KeyError:
                user.promotions = 0
            user.firstName = request.form['fname']
            user.lastName = request.form['lname']
            user.email = request.form['email']
            user.phone = request.form['phone']
            password = request.form['password']

            address = Address(street=request.form['street'], city=request.form['city'], state=request.form['state'],
                              zipcode=request.form['zipcode'])
            if action != 'update_user':
                if adapter.select_user(user.email):
                    current_app.logger.info(f"Already existing user with email: {user.email}.")
                    error_messsage = f"Already existing user with email: {user.email}."
                    return render_template('admin/manage-members.html',
                                           users=[asdict(user) for user in adapter.select_all_users()],
                                           user=None, states=states, user_address=None, edit_user=False, add_user=True,
                                           error_message=error_messsage)
                key, salt = _encrypt_password(password)
                adapter.insert_salt((user.email, salt))
                user.password = key

                if action == 'add_admin':
                    user.isAdmin = 1
                    user.userID = adapter.insert_new_user(user)
                if action == 'add_user':
                    user.isAdmin = 0
                    user.userID = adapter.insert_new_user(user)

                if any([getattr(address, field) != '' for field in address.__dataclass_fields__ if
                        field != 'addressID']):
                    address.addressID = adapter.insert_address(address)
                    adapter.update_user_address(user.userID, address.addressID)

            if action == 'update_user':
                adapter.update_user(user)
                update_address = adapter.select_address(str(user.shippingAddressID))
                if update_address.addressID != -1:
                    address.addressID = update_address.addressID
                    adapter.update_address(address)
                else:
                    if any([getattr(address, field) != '' for field in address.__dataclass_fields__ if
                            field != 'addressID']):
                        address.addressID = adapter.insert_address(address)
                        adapter.update_user_address(user.userID, address.addressID)
                user = adapter.select_user_by_id(user.userID)
                if password != '':
                    key, salt = _encrypt_password(password)
                    adapter.update_salt((salt, user.email))
                    adapter.update_password((key, user.email))
            return render_template('admin/manage-members.html',
                                   users=[asdict(user) for user in adapter.select_all_users()], edit_user=True,
                                   add_user=False, user=asdict(user), states=states,
                                   user_address=asdict(adapter.select_address(user.shippingAddressID)))
    return render_template('admin/manage-members.html', users=[asdict(user) for user in adapter.select_all_users()],
                           user=None, states=states, user_address=None, edit_user=False, add_user=True)


@bp.route('/fees/', methods=('GET', 'POST'))
@admin_required
def manage_fees():
    if request.method == 'POST':
        try:
            adapter.update_child_ticket_price(request.form['child_price'])
            adapter.update_adult_ticket_price(request.form['adult_price'])
            adapter.update_senior_ticket_price(request.form['senior_price'])
        except KeyError:
            try: adapter.update_booking_fee(request.form['booking_fee'])
            except KeyError: current_app.logger.debug('Bad Request')
    return render_template('admin/fees.html', booking_fee=adapter.get_booking_fee()['price'],
                           child_price=adapter.get_child_type().price, adult_price=adapter.get_adult_type().price,
                           senior_price=adapter.get_senior_type().price)


@bp.route('/promo', methods=('GET', 'POST'))
@admin_required
def manage_promo():
    if request.method == 'POST':
        promo_info = {key: request.form.get(key) for key in request.form.keys()}
        # Admin is sending out promo code to users
        try:
            promo = promo_info['selected_promo']
            promotions = adapter.get_promotions()
            discount = 0
            for promo in promotions:
                if promo['code'] == promo:
                    discount = promo['discount']
            promo_recipients = adapter.get_promo_recipients()
            html = render_template('email/promo_email.html', promo_code=promo, discount=discount)
            send_email(to=promo_recipients, subject="New Promotion from Cinema-eBooking!", template=html)
        except KeyError:
            adapter.insert_promotion((promo_info['promo_code'], promo_info['promo_discount']))
    return render_template('admin/promotions.html', promotions=adapter.get_promotions())


@bp.route('/edit-movie/<movie_id>', methods=('GET', 'POST'))
@admin_required
def edit_movie(movie_id: int):
    duration = adapter.get_movie(int(movie_id)).duration
    if request.method == "POST":
        # Delete Showtime
        try:
            showing_id = request.form['showing_id']
            adapter.delete_showing(showing_id)
            return render_template('admin/edit-movie.html', movie=asdict(adapter.get_movie(int(movie_id))),
                                   showings=[asdict(showing) for showing in adapter.get_showings(movie_id)],
                                   all_showings=[asdict(showing) for showing in adapter.get_all_showings()],
                                   genres=adapter.get_genres(), mpaas=adapter.get_mpaa_ratings())
        except KeyError:
            pass
        # Add Showtime
        try:
            dt = datetime.strptime(request.form['showtime'], "%Y-%m-%dT%H:%M")
            showroom = int(request.form['showroom'])
            if not _has_time_conflict(dt, showroom, duration):
                adapter.add_showing((showroom, movie_id, dt, duration))
                return render_template('admin/edit-movie.html', movie=asdict(adapter.get_movie(int(movie_id))),
                                       showings=[asdict(showing) for showing in adapter.get_showings(movie_id)],
                                       all_showings=[asdict(showing) for showing in adapter.get_all_showings()],
                                       genres=adapter.get_genres(), mpaas=adapter.get_mpaa_ratings())
            else:
                error_message = "Showtime Conflict Exists. Shows cannot be overlapping" \
                                " or less than 10 minutes apart. Please retry."
                return render_template('admin/edit-movie.html', movie=asdict(adapter.get_movie(int(movie_id))),
                                       showings=[asdict(showing) for showing in adapter.get_showings(movie_id)],
                                       all_showings=[asdict(showing) for showing in adapter.get_all_showings()],
                                       error_message=error_message, genres=adapter.get_genres(),
                                       mpaas=adapter.get_mpaa_ratings())
        except KeyError:
            pass
        # Update Movie
        try:
            current_app.logger.debug(request.form)
            movie = Movie(movieID=movie_id, title=request.form['title'], genreID=int(request.form['category']),
                          cast=request.form['cast'], director=request.form['director'],
                          producer=request.form['producer'], synopsis=request.form['synopsis'],
                          reviews=float(request.form['reviews']), duration=int(request.form['duration']),
                          trailerPictureLink=request.form['trailer_picture'],
                          trailerVideoLink=request.form['trailer_video'], ratingID=int(request.form['mpaa_id']),
                          release_date=request.form['release_date'])
            if __new_duration_creates_conflicts(movie_id, duration):
                error_message = "Changing duration cause showtime conflict(s). Shows cannot be overlapping or less" \
                                " than 5-10 minutes apart. Please either delete necessary showtimes or fix duration"
                return render_template('admin/edit-movie.html', movie=asdict(adapter.get_movie(int(movie_id))),
                                       showings=[asdict(showing) for showing in adapter.get_showings(movie_id)],
                                       all_showings=[asdict(showing) for showing in adapter.get_all_showings()],
                                       error_message=error_message, genres=adapter.get_genres(),
                                       mpaas=adapter.get_mpaa_ratings())
            current_app.logger.debug("HERE")
            adapter.update_movie(movie)
            return render_template('admin/edit-movie.html', movie=asdict(adapter.get_movie(int(movie_id))),
                                   showings=[asdict(showing) for showing in adapter.get_showings(movie_id)],
                                   all_showings=[asdict(showing) for showing in adapter.get_all_showings()],
                                   genres=adapter.get_genres(), mpaas=adapter.get_mpaa_ratings())
        except KeyError as e:
            current_app.logger.debug(e)
            pass
    return render_template('admin/edit-movie.html', movie=asdict(adapter.get_movie(int(movie_id))),
                           showings=[asdict(showing) for showing in adapter.get_showings(movie_id)],
                           all_showings=[asdict(showing) for showing in adapter.get_all_showings()],
                           genres=adapter.get_genres(), mpaas=adapter.get_mpaa_ratings())


@bp.route('/manage-movie', methods=('GET', 'POST'))
@admin_required
def manage_movie():
    if request.method == 'POST':
        try:
            # Edit/Delete Movie
            movie_id = request.form['selected_movie']
            if movie_id == 'NEW':
                return render_template('admin/manage-movie.html', movies=adapter.get_movies(),
                                       genres=adapter.get_genres(), mpaas=adapter.get_mpaa_ratings())
            if request.form['action'] == 'delete':
                adapter.delete_movie(movie_id)
                return render_template('admin/manage-movie.html', movies=adapter.get_movies(),
                                       genres=adapter.get_genres())
            if request.form['action'] == 'edit':
                return redirect(url_for('admin.edit_movie', movie_id=movie_id))
        except KeyError:
            # Add Movie
            movie = Movie(title=request.form['title'], genreID=int(request.form['genre_id']), cast=request.form['cast'],
                          director=request.form['director'], producer=request.form['producer'],
                          synopsis=request.form['synopsis'], reviews=float(request.form['reviews']),
                          duration=int(request.form['duration']), trailerPictureLink=request.form['trailer_picture'],
                          trailerVideoLink=request.form['trailer_video'], ratingID=int(request.form['mpaa_id']),
                          release_date=request.form['release_date'])
            adapter.insert_movie(movie)
    return render_template('admin/manage-movie.html', movies=adapter.get_movies(), genres=adapter.get_genres(),
                           mpaas=adapter.get_mpaa_ratings())


def _overlaps(start1, finish1, start2, finish2):
    return any([start2 <= start1, start2 < finish1 <= finish2, start1 <= start2 < finish1, start1 < finish2 <= finish1])


def __new_duration_creates_conflicts(movie_id: int, new_duration: int) -> bool:
    showings = adapter.get_all_showings()
    for showing in showings:
        if showing.movieID == int(movie_id):
            showing.duration = new_duration
    for showing in showings:
        for showing2 in showings:
            if showing != showing2:
                finish1 = _round_up_finish_time(showing.datetime + timedelta(minutes=showing.duration))
                finish2 = _round_up_finish_time(showing2.datetime + timedelta(minutes=showing.duration))
                if _overlaps(showing.datetime, finish1, showing2.datetime, finish2): return True
    return False


def _round_up_finish_time(dt):
    return (dt + (datetime.min - dt) % timedelta(minutes=5)) + timedelta(minutes=5)


def _has_time_conflict(dt: datetime, showroom: int, duration: int) -> bool:
    showings = adapter.get_all_showings()
    for showing in showings:
        showing_dt = showing.datetime
        if showing.showRoomID == showroom:
            finish1 = _round_up_finish_time(showing_dt + timedelta(minutes=showing.duration))
            finish2 = _round_up_finish_time(dt + timedelta(minutes=duration))
            return _overlaps(showing_dt, finish1, dt, finish2)
    return False
