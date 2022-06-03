const container = document.querySelector('.container');
const seats = document.querySelectorAll('.row .seat:not(.occupied)');
const count = document.getElementById('count');
const total = document.getElementById('total');
const movieSelect = document.getElementById('movie');

let ticketQuantity = 0;
let numTicketsSelected = 0;
populateUI();

let ticketPrice = +movieSelect.value;

// Save selected movie index and price
function setMovieData(movieIndex, moviePrice) {
    localStorage.setItem('selectedMovieIndex', movieIndex);
    localStorage.setItem('selectedMoviePrice', moviePrice);
}

// Update total and count
function updateSelectedCount() {
    const selectedSeats = document.querySelectorAll('.row .seat.selected');

    const seatsIndex = [...selectedSeats].map(seat => [...seats].indexOf(seat));

    localStorage.setItem('selectedSeats', JSON.stringify(seatsIndex));

    const selectedSeatsCount = selectedSeats.length;

    count.innerText = selectedSeatsCount;
    total.innerText = selectedSeatsCount * ticketPrice;

    setMovieData(movieSelect.selectedIndex, movieSelect.value);
}

// Get data from localstorage and populate UI
function populateUI() {
    const selectedSeats = JSON.parse(localStorage.getItem('selectedSeats'));
    const selectedMovieIndex = localStorage.getItem('selectedMovieIndex');

    if (selectedMovieIndex !== null) {
        movieSelect.selectedIndex = selectedMovieIndex;
    }
}

// Movie select event
movieSelect.addEventListener('change', e => {
    ticketPrice = +e.target.value;
    setMovieData(e.target.selectedIndex, e.target.value);
    updateSelectedCount();
});

// Seat click event
container.addEventListener('click', e => {
    if (
        e.target.classList.contains('seat') &&
        !e.target.classList.contains('occupied')
    ) {


        const selectedSeats = document.querySelectorAll('.row .seat.selected');

        // deselecting an already selected seat
        if (e.target.classList.contains('selected')) {
            if (numTicketsSelected != 0) numTicketsSelected--;
            e.target.classList.toggle('selected');
            updateSelectedCount();
            console.log("ticks selected " + numTicketsSelected);
            console.log("tick quant " + ticketQuantity);
        }
        // selecting an available seat and they still have tickets to assign seats to...
        else if (numTicketsSelected < ticketQuantity) {
            numTicketsSelected++;
            e.target.classList.toggle('selected');
            updateSelectedCount();
             console.log("ticks selected " + numTicketsSelected);
            console.log("tick quant " + ticketQuantity);
        }

    }
});

// Initial count and total set
updateSelectedCount();

function setTicketQuantity(quantity) {
    ticketQuantity = quantity;
}

function sendSeatData() {
    var jsonData = {
        "seats": []
    };
    const selectedSeats = document.querySelectorAll('.row .seat.selected');
    console.log(selectedSeats)
    for (let i = 0; i < selectedSeats.length; i++) {
        seat = selectedSeats[i]
        rowLetter = seat.getAttribute('row');
        seatNum = seat.getAttribute('number');
        jsonData.seats.push({
            'rowLetter': rowLetter,
            'seatNum': seatNum
        });
    }

    $.post(window.location.pathname, {
        seats: JSON.stringify(jsonData)
    }, function(data) {
        console.log(data)
        window.location.pathname = data
    });

}