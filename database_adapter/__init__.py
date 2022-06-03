import random
import string
from datetime import datetime
from typing import List, Union

import mysql.connector

from configuration import config
from models import User, Movie, Showing, Seat, Ticket, Booking, TicketType, Address

db_auth = config['db_auth']


class DatabaseAdapter:
    """Encapsulates call MySQL queries needed in the Cinema-eBooking project."""

    def __init__(self, **kwargs):
        self._connection = mysql.connector.connect(**kwargs)
        self._cursor = self._connection.cursor(dictionary=True, buffered=True)

    def insert_movie(self, movie: Movie):
        query = """INSERT INTO movie (title, genreID, cast, director, producer, synopsis, reviews, duration, 
        trailerPictureLink, trailerVideoLink, ratingID, release_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        params = (movie.title, movie.genreID, movie.cast, movie.director, movie.producer, movie.synopsis, movie.reviews,
                  movie.duration, movie.trailerPictureLink, movie.trailerVideoLink, movie.ratingID, movie.release_date)
        self._execute_query(query, params)

    def insert_movies(self, movies: List[tuple]):
        query = """INSERT INTO movie (title, genreID, cast, director, producer, synopsis, reviews, duration, 
        trailerPictureLink, trailerVideoLink, ratingID, release_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"""
        self._execute_query(query, movies)

    def get_movie(self, movie_id: int) -> Union[bool, Movie]:
        query = """SELECT * FROM moviebookings.movie WHERE movieID = %s"""
        self._execute_query(query, (movie_id,))
        movie = self._cursor.fetchone()
        return False if not movie else Movie(**movie)

    def get_movies_like_title(self, title: str) -> list:
        query = f"""SELECT * FROM moviebookings.movie WHERE title LIKE '%{title}%'"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def get_movies(self) -> list:
        query = """SELECT * FROM moviebookings.movie"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def get_released_movie(self, title) -> list:
        query = f"""SELECT * FROM moviebookings.movie WHERE title LIKE '%{title}%' AND CURDATE() >= release_date"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def get_coming_soon_movie(self, title):
        query = f"""SELECT * FROM moviebookings.movie WHERE title LIKE '%{title}%' AND CURDATE() < release_date"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def get_coming_soon_movies(self) -> list:
        query = """SELECT * FROM moviebookings.movie WHERE CURDATE() < release_date"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def get_released_movies(self) -> list:
        query = f"""SELECT * FROM moviebookings.movie WHERE CURDATE() >= release_date"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def update_movie(self, movie: Movie):
        query = """UPDATE moviebookings.movie SET title = %s, genreID = %s, cast = %s, director = %s, producer = %s, 
        synopsis = %s, reviews = %s, duration = %s, trailerPictureLink = %s, trailerVideoLink = %s, ratingID = %s, 
        release_date = %s WHERE movieID = %s"""
        params = (movie.title, movie.genreID, movie.cast, movie.director, movie.producer, movie.synopsis, movie.reviews,
                  movie.duration, movie.trailerPictureLink, movie.trailerVideoLink, movie.ratingID, movie.release_date,
                  movie.movieID)
        self._execute_query(query, params)
        query = """UPDATE moviebookings.showing SET duration = %s WHERE movieID = %s"""
        self._execute_query(query, (movie.duration, movie.movieID))

    def delete_movie(self, movie_id: int):
        query = """DELETE FROM moviebookings.movie where movieID = %s"""
        self._execute_query(query, (movie_id,))

    def insert_mpaa_ratings(self, ratings):
        query = """INSERT INTO usrating (ratingCode) VALUES (%s)"""
        self._execute_query_ridiculous(query, ratings)

    def get_mpaa_rating_id(self, rating):
        query = """SELECT ratingID FROM usrating WHERE ratingCode=%s """
        self._execute_query(query, (rating,))
        return self._cursor.fetchone()['ratingID']

    def get_mpaa_ratings(self):
        query = """SELECT * FROM usrating"""
        self._execute_query_ridiculous(query)
        return self._cursor.fetchall()

    def get_mpaa_rating(self, rating_id) -> str:
        query = """SELECT ratingCode FROM usrating WHERE ratingID=%s"""
        self._execute_query(query, (rating_id,))
        return self._cursor.fetchone()['ratingCode']

    def get_showings(self, movie_id: int) -> List[Showing]:
        query = """SELECT * from showing where movieID = %s"""
        self._execute_query(query, (movie_id,))
        return [Showing(**showing) for showing in self._cursor.fetchall()]

    def get_showing(self, show_id: int) -> Showing:
        query = """SELECT * FROM showing WHERE showID=%s"""
        self._execute_query(query, (show_id,))
        return Showing(**self._cursor.fetchone())

    def get_all_showings(self) -> List[Showing]:
        query = """SELECT * from showing"""
        self._execute_query(query)
        return [Showing(**showing) for showing in self._cursor.fetchall()]

    def add_showing(self, tup: tuple):
        query = """INSERT INTO showing (showRoomID, movieID, datetime, duration) VALUES (%s,%s,%s,%s)"""
        self._execute_query(query, tup)

    def get_shows_on_date(self, date: datetime, movie_id) -> List[dict]:
        query = """SELECT * FROM showing WHERE movieID=%s AND datetime=%s"""
        self._execute_query(query, (movie_id, date))
        return list(self._cursor.fetchall())

    def delete_showing(self, showing_id: int):
        query = """DELETE FROM showing WHERE showID = %s"""
        self._execute_query(query, (showing_id,))

    def insert_payment_card(self, tup: tuple) -> int:
        query = """INSERT INTO paymentcard (firstName, lastName, cardType, cardNumber, billingAddressID, 
        expirationMonth, expirationYear, userID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        self._execute_query_ridiculous(query, tup)
        return self._cursor.lastrowid

    def get_paymentcard(self, id: int) -> dict:
        query = """SELECT * FROM paymentcard WHERE paymentID = %s"""
        self._execute_query_ridiculous(query, (id,))
        return self._cursor.fetchone()

    def get_paymentcards(self, id: int) -> List[dict]:
        query = """SELECT * FROM paymentcard WHERE userID = %s"""
        self._execute_query(query, (id,))
        return list(self._cursor.fetchall())

    def delete_paymentcard(self, id: int):
        query = """DELETE FROM paymentcard WHERE paymentID = %s"""
        self._execute_query(query, (id,))

    def delete_address(self, id: int):
        query = """DELETE FROM paymentcard WHERE billingAddressID = %s"""
        self._execute_query_ridiculous(query, (id,))

    def update_address(self, address: Address):
        query = """UPDATE address SET street = %s, city = %s, state = %s, zipcode = %s WHERE addressID = %s"""
        params = (address.street, address.city, address.state, address.zipcode, address.addressID)
        self._execute_query(query, params)

    def select_address(self, address_id: str) -> Union[bool, Address]:
        query = """SELECT * FROM address WHERE addressID = %s"""
        self._execute_query(query, (address_id,))
        address = self._cursor.fetchone()
        return Address() if not address else Address(**address)

    def insert_address(self, address: Address) -> int:
        query = """INSERT INTO address (street, city, state, zipcode) VALUES(%s,%s,%s,%s)"""
        params = (address.street, address.city, address.state, address.zipcode)
        self._execute_query(query, params)
        return self._cursor.lastrowid

    def insert_new_user(self, user: User):
        query = """INSERT INTO user (firstName, lastName, email, password, phone, isAdmin, isSuspended, promotions, email_confirmed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        params = (user.firstName, user.lastName, user.email, user.password, user.phone, user.isAdmin, user.isSuspended,
                  user.promotions, user.email_confirmed)
        self._execute_query(query, params)
        return self._cursor.lastrowid

    def insert_new_user_tup(self, params: tuple):
        query = """INSERT INTO user (firstName, lastName, email, password, phone, isAdmin, isSuspended, promotions, email_confirmed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self._execute_query(query, params)

    def update_user(self, user: User):
        query = """UPDATE user SET firstName = %s, lastName = %s, email = %s, email_confirmed = %s, password = %s, 
        phone = %s, promotions = %s, shippingAddressID = %s, isAdmin = %s, isSuspended = %s WHERE userID = %s"""
        params = (
            user.firstName, user.lastName, user.email, user.email_confirmed, user.password, user.phone, user.promotions,
            user.shippingAddressID, user.isAdmin, user.isSuspended, user.userID)
        self._execute_query(query, params)

    def update_user_address(self, user_id: int, address_id: int):
        vals = (address_id, user_id)
        query = """UPDATE user SET shippingAddressID = %s WHERE userID = %s"""
        self._execute_query(query, vals)

    def suspend_user(self, user_id: int):
        query = """UPDATE user SET isSuspended = 1 WHERE userID = %s """
        self._execute_query_ridiculous(query, (user_id,))

    def unsuspend_user(self, user_id: int):
        query = """UPDATE user SET isSuspended = 0 WHERE userID = %s """
        self._execute_query_ridiculous(query, (user_id,))

    def select_user(self, email: str) -> Union[bool, User]:
        if email is None:
            return False
        query = """SELECT * FROM user WHERE email = %s"""
        self._execute_query(query, (email,))
        user = self._cursor.fetchone()
        return False if not user else User(**user)

    def select_user_by_id(self, user_id: int) -> Union[bool, User]:
        query = """SELECT * FROM user WHERE userID = %s"""
        self._execute_query(query, (user_id,))
        user = self._cursor.fetchone()
        return False if not user else User(**user)

    def select_all_users(self) -> List[User]:
        query = """SELECT * FROM user"""
        self._execute_query(query)
        return [User(**user) for user in self._cursor.fetchall()]

    def select_admin(self, email: str) -> Union[bool, User]:
        query = """SELECT * FROM user WHERE email = %s and isAdmin = 1"""
        self._execute_query_ridiculous(query, (email,))
        user = self._cursor.fetchone()
        return False if not user else User(**user)

    def get_salt(self, key: str) -> str:
        query = """SELECT * FROM salts WHERE email = %s"""
        self._execute_query(query, (key,))
        return self._cursor.fetchone()['salt']

    def insert_salt(self, tup: tuple):
        query = """INSERT INTO salts (email, salt) VALUES (%s,%s)"""
        self._execute_query(query, tup)

    def update_salt(self, tup: tuple):
        query = f"""UPDATE salts
                SET salt = %s
                WHERE email = %s"""
        self._execute_query(query, tup)

    def set_email_confirmed(self, email: str):
        query = """UPDATE user SET email_confirmed = true WHERE email = %s"""
        self._execute_query(query, (email,))

    def get_email_confirmed(self, email: str) -> bool:
        query = """SELECT email_confirmed FROM user WHERE email = %s"""
        self._execute_query_ridiculous(query, (email,))
        try:
            return bool(self._cursor.fetchone()['email_confirmed'])
        except:
            return False

    def update_password(self, tup: tuple):
        query = f"""UPDATE user
                SET password = %s
                WHERE email = %s"""
        self._execute_query(query, tup)

    def insert_promotion(self, tup: tuple):
        query = """INSERT INTO promotion (code, discount) VALUES (%s, %s)"""
        self._execute_query_ridiculous(query, tup)

    def get_promotions(self) -> List[dict]:
        query = """SELECT * FROM promotion"""
        self._execute_query(query)
        return list(self._cursor.fetchall())

    def get_promo_recipients(self) -> List[str]:
        query = """SELECT email FROM user WHERE promotions = true"""
        self._execute_query(query)
        return [user['email'] for user in self._cursor.fetchall()]

    def get_genres(self):
        query = """SELECT * FROM genre"""
        self._execute_query(query)
        return self._cursor.fetchall()

    def get_genre(self, genre_id) -> str:
        query = """SELECT genre FROM genre WHERE genreID=%s"""
        self._execute_query(query, (genre_id,))
        return self._cursor.fetchone()['genre']

    def get_genre_id(self, genre) -> int:
        query = """SELECT genreID FROM genre WHERE genre=%s"""
        self._execute_query_ridiculous(query, (genre,))
        return self._cursor.fetchone()['genreID']

    def get_movies_by_genre_id(self, genre_id) -> List[dict]:
        query = """SELECT * FROM movie WHERE genreID=%s"""
        self._execute_query(query, (genre_id,))
        return list(self._cursor.fetchall())

    def seat_is_taken(self, seat: Seat) -> bool:
        query = """SELECT * FROM seat WHERE rowLetter=%s, seatNum=%s, showroomID=%s"""
        self._execute_query_ridiculous(query, (seat.rowLetter, seat.seatNum, seat.showRoomID))
        return bool(self._cursor.fetchone()['ticketID'])

    def get_available_seats_in_showroom(self, showroom_id: int) -> List[Seat]:
        query = """SELECT * FROM seat WHERE showroomID=%s AND (ticketID IS NULL OR ticketID < 0)"""
        self._execute_query(query, (showroom_id,))
        return [Seat(**seat) for seat in self._cursor.fetchall()]

    def get_selected_seats(self, showroom_id, row_letter, seat_num) -> Seat:
        query = """SELECT * FROM seat WHERE showroomID=%s AND rowLetter=%s AND seatNum=%s"""
        self._execute_query(query, (showroom_id, row_letter, seat_num))
        return Seat(**self._cursor.fetchone())

    def set_seat_taken(self, seat_id: int, ticket_id: int):
        query = """UPDATE seat SET ticketID=%s WHERE seatID=%s"""
        self._execute_query(query, (ticket_id, seat_id))

    def get_seats_in_showroom(self, showroom_id: int) -> List[Seat]:
        query = """SELECT * FROM seat WHERE showRoomID=%s"""
        self._execute_query(query, (showroom_id,))
        return [Seat(**seat) for seat in self._cursor.fetchall()]

    def insert_ticket(self, ticket: Ticket) -> int:
        query = """INSERT INTO ticket (typeID, bookingID, seatID) VALUES (%s,%s,%s)"""
        self._execute_query_ridiculous(query, (ticket.typeID, ticket.bookingID, ticket.seatID))
        return self._cursor.lastrowid

    def get_ticket_types(self) -> List[TicketType]:
        query = """SELECT * FROM tickettype"""
        self._execute_query(query)
        return [TicketType(**tt) for tt in self._cursor.fetchall()]

    def get_adult_type(self) -> TicketType:
        query = """SELECT * FROM tickettype WHERE ticketTypeName = 'Adult'"""
        self._execute_query(query)
        return TicketType(**self._cursor.fetchone())

    def get_child_type(self) -> TicketType:
        query = """SELECT * FROM tickettype WHERE ticketTypeName = 'Child'"""
        self._execute_query(query)
        return TicketType(**self._cursor.fetchone())

    def get_senior_type(self) -> TicketType:
        query = """SELECT * FROM tickettype WHERE ticketTypeName = 'Senior'"""
        self._execute_query(query)
        return TicketType(**self._cursor.fetchone())

    def update_child_ticket_price(self, price: float):
        query = """UPDATE tickettype SET price = %s WHERE ticketTypeName = 'Child'"""
        self._execute_query(query, (price,))

    def update_adult_ticket_price(self, price: float):
        query = """UPDATE tickettype SET price = %s WHERE ticketTypeName = 'Adult'"""
        self._execute_query(query, (price,))

    def update_senior_ticket_price(self, price: float):
        query = """UPDATE tickettype SET price = %s WHERE ticketTypeName = 'Senior'"""
        self._execute_query(query, (price,))

    def update_booking_fee(self, fee: float):
        query = """UPDATE bookingfees SET price = %s WHERE bookingFeeID = 1"""
        self._execute_query(query, (fee,))

    def get_booking_fee(self) -> List[dict]:
        query = """SELECT * FROM bookingfees"""
        self._execute_query(query)
        return self._cursor.fetchone()

    def insert_booking(self, booking: Booking) -> int:
        query = """INSERT INTO booking (userID, showingID, paymentID, noOfTickets, totalPrice, promoID, bookingTime) 
        VALUES (%s,%s,%s,%s,%s,%s,%s) """
        self._execute_query(query, (
            booking.userID, booking.showingID, booking.paymentID, booking.noOfTickets, booking.totalPrice,
            booking.promoID, booking.bookingTime))
        return self._cursor.lastrowid

    def get_seats_from_booking(self, booking: Booking) -> List[Seat]:
        query = """SELECT * FROM seat WHERE seatID IN (SELECT seatID FROM ticket WHERE bookingID = %s)"""
        alternative_query = """SELECT DISTINCT seat.seatID,rowLetter,seatNum,showRoomID,seat.ticketID FROM seat LEFT JOIN 
        ticket ON seat.seatID=ticket.seatID WHERE bookingID = %s """
        query = query if random.randint(0, 1) else alternative_query
        self._execute_query(query, (booking.bookingID,))
        return [Seat(**seat) for seat in self._cursor.fetchall()]

    def get_order_history(self, user: User) -> List[Booking]:
        query = """SELECT * FROM booking WHERE userID=%s"""
        self._execute_query(query, (user.userID,))
        return [Booking(**booking) for booking in self._cursor.fetchall()]

    def _execute_query_ridiculous(self, query: str, params=None):
        """A far less readable (but cooler looking) version of _execute_query."""
        self._cursor.executemany(query, params) if params and any(
            [type(params) == set, type(params) == list]) else self._cursor.execute(query,
                                                                                   params) if params else self._cursor.execute(
            query)
        self._connection.commit()

    def _execute_query(self, query: str, params=None):
        """Helper method to automate query execution. Works for execute and executemany.
        :param query: The SQL to execute.
        :param params: The parameter(s) to the query.
        Parameters for execute many should be list or set,
        and for one execution should be a tuple.
        :note: Does not fetch query results."""
        if params and any([type(params) == set, type(params) == list]):
            self._cursor.executemany(query, params)
        else:
            self._cursor.execute(query, params) if params else self._cursor.execute(query)
        self._connection.commit()

    def _populate_theatre(self, num_theatres):
        for i in range(num_theatres):
            sql = "INSERT INTO moviebookings.theatre (buildingID) VALUES (%s)"
            val = (i,)
            self._execute_query(sql, val)

    def _populate_showroom(self, num_showrooms_per_theatre, num_rows_per_showroom, num_seats_per_row, num_theatres):
        for i in range(num_showrooms_per_theatre * num_theatres):
            sql = """INSERT INTO moviebookings.showroom (showroomID, theatreID, noOfSeats) VALUES (%s,%s,%s)"""
            val = (i, i % num_theatres, num_rows_per_showroom * num_seats_per_row)
            self._execute_query(sql, val)

    def _populate_seats(self, num_showrooms_per_theatre, num_rows_per_showroom, num_seats_per_row, num_theatres):
        seat_id = 0
        row_letters = list(string.ascii_uppercase)[0:num_rows_per_showroom]
        for room in range(num_showrooms_per_theatre * num_theatres):
            for row in range(num_rows_per_showroom):
                for seat in range(num_seats_per_row):
                    sql = """INSERT INTO moviebookings.seat (seatID, rowLetter, seatNum, showRoomID, ticketID) VALUES 
                    (%s,%s,%s,%s,%s) """
                    val = (seat_id, row_letters[row], seat + 1, room, None)
                    self._execute_query(sql, val)
                    seat_id += 1

    def setup(self):
        num_theatres = 1
        num_showrooms_per_theatre = 6

        num_rows_per_showroom = 8
        num_seats_per_row = 8

        # Clear tables
        self._execute_query('DELETE FROM moviebookings.seat')
        self._execute_query('DELETE FROM moviebookings.showroom')
        self._execute_query('DELETE FROM moviebookings.theatre')
        self._populate_theatre(num_theatres)
        self._populate_showroom(num_showrooms_per_theatre, num_rows_per_showroom, num_seats_per_row, num_theatres)
        self._populate_seats(num_showrooms_per_theatre, num_rows_per_showroom, num_seats_per_row, num_theatres)


adapter = DatabaseAdapter(**db_auth)
