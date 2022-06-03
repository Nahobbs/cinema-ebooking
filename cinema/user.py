import hashlibimport osfrom dataclasses import asdictfrom datetime import datetimefrom functools import wrapsfrom flask import (Blueprint, request, render_template, current_app, url_for, redirect, session)from database_adapter import adapterfrom models import User, Addressbp = Blueprint('user', __name__, url_prefix='/user')def login_required(func):    @wraps(func)    def wrapper(*args, **kwargs):        try:            user = adapter.select_user(session['user_email'])            return func(*args, **kwargs) if user else redirect(url_for('user.login'))        except KeyError:            # user needs to log in            return redirect(url_for('user.login'))    return wrapper@bp.route('/register', methods=('GET', 'POST'))@bp.route('/login', methods=('GET', 'POST'))def login():    if request.method == 'POST':        try:            # resetting password            email = request.form['email_forgot_password']            current_app.logger.info("User resetting password.")            return redirect(url_for('email.send_password_reset_email', user_email=email))        except KeyError:            try:                # logging in                return _handle_login()            except KeyError:                # registration                return _handle_registration()    remember_me = True if session.get('remember_me') else False    user = adapter.select_user(session.get('user_email'))    if user and user.isAdmin and remember_me:        return redirect(url_for('admin.view'))    return redirect(url_for('user.view')) if remember_me and user else render_template('user/user-signin-signup.html')@bp.route('/search', methods=('GET', 'POST'))def search():    session['in_progress'] = True    # user is searching    if request.method == 'POST':        current_app.logger.info("User is searching")        # user is searching by title        try:            movies = _handle_search()            return render_template('user/search-movie.html', genres=adapter.get_genres(), movies=movies)        # user is searching by genre        except KeyError:            movies = adapter.get_movies_by_genre_id(request.form['genreID'])            return render_template('user/search-movie.html', genres=adapter.get_genres(), movies=movies)    return render_template('user/search-movie.html', genres=adapter.get_genres())@bp.route('/logout', methods=['GET'])@login_requireddef logout():    [session.pop(key) for key in list(session.keys())]    session.clear()    return redirect(url_for('user.login'))@bp.route('/change-pwd', methods=('GET', 'POST'))@login_requireddef change_password():    session['in_progress'] = True    if request.method == 'POST':        email = session.get('user_email')        try:            # user editing profile            current_password = request.form['current_password']            if not _decrypt_password(email, current_password, adapter.select_user(email)):                current_app.logger.info("Current Password incorrect.")                return render_template('user/change-pwd.html', reset=False)            return _change_password(email, request.form['password'])        except KeyError:            # user forgot password            return _change_password(email, request.form['password'])    reset_password = session.get('RESET_PASSWORD') if session.get('RESET_PASSWORD') else False    return render_template('user/change-pwd.html', reset=reset_password)@bp.route('/manage-payment', methods=('GET', 'POST'))@login_requireddef manage_payment():    session['in_progress'] = True    checking_out = session.get('checking_out')    user = adapter.select_user(session['user_email'])    payment_cards = adapter.get_paymentcards(user.userID)    if request.method == 'POST':        card_info = {key: request.form.get(key) for key in request.form.keys()}        current_app.logger.info(f"User {user.email} managing payment cards")        # user entering new payment card        if request.form['selected_card'] == "NEW":            # TODO verify credit card w/ CVV --- CVV not saved in database            valid = True            if valid:                address_id = adapter.insert_address(                    Address(street=card_info['street'], city=card_info['city'], state=card_info['state'],                            zipcode=card_info['zipcode']))                adapter.insert_payment_card((                    card_info['fname'], card_info['lname'], card_info['card_type'], card_info['card_number'],                    address_id, card_info['month'], card_info['year'], user.userID))            else:                current_app.logger.info('bad payment info')        # user updating an existing payment card        else:            current_app.logger.info("Updating payment card.}")            _update_paymentcard(card_info['card_number'], card_info['card_type'], card_info['city'], card_info['month'],                                card_info['year'], card_info['fname'], card_info['lname'], card_info['state'],                                card_info['street'], user.userID, card_info['zipcode'])        payment_cards = adapter.get_paymentcards(user.userID)        return render_template('user/paymentmethod.html', payment_cards=payment_cards, year='', state='', month='',                               card_type='', checking_out=checking_out)    current_app.logger.info(f"User {user.email} viewing payment cards")    return render_template('user/paymentmethod.html', payment_cards=payment_cards, year='', state='', month='',                           card_type='', checking_out=checking_out)@bp.route('/edit-profile', methods=('GET', 'POST'))@login_requireddef edit_profile():    session['in_progress'] = True    user = adapter.select_user(session['user_email'])    current_app.logger.info(f"User {user.email} editing profile")    if request.method == 'POST':        try:            user.firstName = request.form['firstName']            user.lastName = request.form['lastName']            user.phone = request.form['phone']            adapter.update_user(user)        except KeyError:            user_address = Address(street=request.form['street'], zipcode=request.form['zipcode'],                                   city=request.form['city'], state=request.form['state'])            update_address = adapter.select_address(str(user.shippingAddressID))            if update_address.addressID != -1:                user_address.addressID = update_address.addressID                adapter.update_address(user_address)            else:                address_id = adapter.insert_address(user_address)                adapter.update_user_address(user.userID, address_id)    user = adapter.select_user(session['user_email'])    return render_template('user/edit-info.html', user=asdict(user),                           user_address=asdict(adapter.select_address(str(user.shippingAddressID))))@bp.route('/view', methods=('GET', 'POST'))def view():    current_app.logger.info('User browsing.')    session['checking_out'] = False    movies_out = adapter.get_released_movies()    coming_soon = adapter.get_coming_soon_movies()    logged_in = session.get('user_email')    print(logged_in)    return render_template('user/user-view-signed-in.html', movies_out=movies_out, coming_soon=coming_soon,                           logged_in=logged_in)@bp.route('/movie_info/<movie_id>/', methods=('GET', 'POST'))def movie_info(movie_id):    session['in_progress'] = True    current_app.logger.info(f'User viewing movie info for movie {movie_id}.')    session['checking_out'] = False    movie = adapter.get_movie(movie_id)    movie_dict = asdict(movie)    video_link = movie.trailerVideoLink    try:        video_link = video_link[video_link.index('=') + 1:]    except:        video_link = ""    movie_dict['trailerVideoLink'] = video_link    movie_dict['genre'] = adapter.get_genre(movie.genreID)    movie_dict['mpaa'] = adapter.get_mpaa_rating(movie.ratingID)    return render_template('user/movie_info.html', movie=movie_dict)@bp.route('/show_timing/<movie_id>/', methods=('GET', 'POST'))def show_timing(movie_id):    session['in_progress'] = True    current_app.logger.info(f'User viewing show times for movie {movie_id}.')    session['checking_out'] = False    showtimes = {}    date = None    if request.method == 'POST':        showings = adapter.get_all_showings()        date = datetime.strptime(request.form['show_date'], "%Y-%m-%d").date()        showings_filtered = [showing for showing in showings if                             showing.datetime.date() == date and showing.movieID == int(movie_id)]        showtimes = {showing.showID: showing.datetime.strftime('%I:%M %p') for showing in showings_filtered}    return render_template('user/show_timing.html', movie=asdict(adapter.get_movie(movie_id)), showtimes=showtimes,                           date=date)@bp.route('/order_history/', methods=('GET', 'POST'))@login_requireddef order_history():    bookings = adapter.get_order_history(adapter.select_user(session['user_email']))    order_history = []    for booking in bookings:        order = {}        showing = adapter.get_showing(booking.showingID)        movie = adapter.get_movie(showing.movieID)        order['title'] = movie.title        order['booking_id'] = str(booking.bookingID).zfill(8)        order['order_time'] = booking.bookingTime.strftime('%m/%d/%Y %I:%M:%S %p')        order['num_tickets'] = booking.noOfTickets        order['showroom'] = showing.showRoomID        order['showtime'] = showing.datetime.strftime('%m/%d/%Y %I:%M %p')        order['total'] = booking.totalPrice        order['seats'] = ",".join([f"{seat.rowLetter}{seat.seatNum}" for seat in adapter.get_seats_from_booking(booking)])        paymentcard = adapter.get_paymentcard(booking.paymentID)        cnum = str(paymentcard['cardNumber'])        order['payment'] = f"{paymentcard['cardType']} - {cnum[-4:].rjust(len(cnum), 'X')}"        order_history.append(order)    return render_template('user/order_history.html', order_history=order_history)def _handle_registration():    first_name, last_name = request.form['fname'], request.form['lname']    password = request.form['password1']    email = request.form['email_signup']    phone_num = request.form['phone']    promo = True if request.form.get('subscribe') else False    if adapter.select_user(email):        current_app.logger.info(f"Already existing user with email: {email}.")        return render_template('user/user_dne.html')    # insert the new user    key, salt_str = _encrypt_password(password)    adapter.insert_salt((email, salt_str))    user = User(firstName=first_name, lastName=last_name, email=email, password=key, phone=phone_num, isAdmin=0,                isSuspended=0, promotions=promo, email_confirmed=False)    adapter.insert_new_user(user)    return redirect(url_for('email.confirm_email', user_email=email))def _handle_login():    email = request.form['email_signin']    password = request.form['password']    remember_me = True if request.form.get('remember-me') else False    user = adapter.select_user(email)    current_app.logger.debug(user)    session['RESET_PASSWORD'] = False    if not user:        error_message = f"Account for {email} does not exist"        current_app.logger.info(error_message)        return render_template('user/user-signin-signup.html', error_message=error_message)    if not _decrypt_password(email, password, user):        error_message = "Incorrect Password"        current_app.logger.info(error_message)        return render_template('user/user-signin-signup.html', error_message=error_message)    elif not user.email_confirmed:        current_app.logger.info(f"{email} needs to confirm email.")        return redirect(url_for('email.confirm_email', user_email=email))    elif user.isSuspended:        error_message = "Your account has been suspended. Please contact administration for support."        return render_template('user/user-signin-signup.html', error_message=error_message)    elif user.isAdmin:        session['user_email'] = email        session['remember_me'] = remember_me        return redirect(url_for('admin.view'))    else:        session['remember_me'] = remember_me        session['user_email'] = email        return redirect(url_for('user.view'))def _handle_search():    search_params = {key: request.form.get(key) for key in request.form.keys()}    if search_params['category'] == 'Released':        print(search_params['movie_title'])        movies = adapter.get_released_movie(search_params['movie_title'])    elif search_params['category'] == 'Coming Soon':        movies = adapter.get_coming_soon_movie(search_params['movie_title'])    else:        movies = adapter.get_movies_like_title(search_params['movie_title'])    return moviesdef _update_paymentcard(card_number, card_type, city, exp_month, exp_year, fname, lname, state, street, user_id,                        zipcode):    payment_card_id = int(request.form['selected_card'])    address_id = adapter.get_paymentcard(payment_card_id)['billingAddressID']    adapter.delete_paymentcard(payment_card_id)    adapter.delete_address(address_id)    address_id = adapter.insert_address((street, city, state, zipcode))    adapter.insert_payment_card((fname, lname, card_type, card_number, address_id, exp_month, exp_year, user_id))def _change_password(email, password):    key, salt = _encrypt_password(password)    adapter.update_salt((salt, email))    adapter.update_password((key, email))    current_app.logger.info(f"Changed password for {email}")    return redirect(url_for('user.login'))def _encrypt_password(password):    salt = os.urandom(32)    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).decode(encoding='unicode_escape')    return key, salt.decode(encoding='unicode_escape')def _decrypt_password(email, password, user):    current_app.logger.debug((email, password, user))    salt = adapter.get_salt(email).encode(encoding='raw_unicode_escape')    key = user.password.encode(encoding='raw_unicode_escape')    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)    return key == new_key