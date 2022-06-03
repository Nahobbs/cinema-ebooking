import datetime
from dataclasses import dataclass
from typing import Union


@dataclass
class User:
    firstName: str = ""
    lastName: str = ""
    email: str = ""
    email_confirmed: bool = False
    password: str = ""
    phone: str = ""
    promotions: bool = False
    isAdmin: bool = False
    isSuspended: bool = False
    shippingAddressID: int = -1
    userID: int = -1


@dataclass
class Movie:
    title: str
    genreID: int
    cast: str
    director: str
    producer: str
    synopsis: str
    reviews: float
    duration: int
    trailerPictureLink: str
    trailerVideoLink: str
    ratingID: int
    release_date: Union[datetime.datetime, str]
    movieID: int = -1


@dataclass
class Showing:
    showRoomID: int
    movieID: int
    datetime: datetime.datetime
    duration: int
    showID: int = -1


@dataclass
class PaymentCard:
    firstName: str
    lastName: str
    cardType: str
    cardNumber: int
    expirationMonth: int
    expirationYear: int
    userID: int = -1
    paymentID: int = -1
    billingAddressID: int = -1


@dataclass
class Booking:
    userID: int
    showingID: int
    noOfTickets: int
    bookingTime: Union[datetime.datetime, str]
    promoID: int = -1
    bookingID: int = -1
    paymentID: int = -1
    totalPrice: float = -1


@dataclass
class Ticket:
    typeID: int
    seatID: int
    ticketID: int = -1
    bookingID: int = -1


@dataclass
class TicketType:
    ticketTypeID: int
    price: float
    ticketTypeName: str


@dataclass
class Seat:
    seatID: int
    rowLetter: str
    seatNum: int
    showRoomID: int
    ticketID: Union[int, None]


@dataclass
class Address:
    addressID: int = -1
    street: str = ''
    state: str = ''
    city: str = ''
    zipcode: int = ''
