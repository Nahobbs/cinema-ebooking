var scrollPerClickOut, scrollPerClickComing;
var ImagePadding = 20;
const d = new Date();

var date = d.getFullYear() + "-" + (d.getMonth() + 1)  + "-" + d.getDate();
console.log(date)

// populateOutNow();
populateComing();

var scrollAmount = 0;

function sliderScrollLeft(a) {
  console.log("scrolling left")
  const sliders = document.querySelector("."+ a);
  sliders.scrollTo({
    top: 0,
    left: (scrollAmount -= scrollPerClick),
    behavior: "smooth"
  });

  if(scrollAmount < 0) {
    scrollAmount = 0
  }
}

function sliderScrollRight(a) {
  console.log("scrolling right")
  const sliders = document.querySelector("."+ a);
  if(scrollAmount <= sliders.scrollWidth - sliders.clientWidth) {
    sliders.scrollTo({
      top: 0,
      left: (scrollAmount += scrollPerClick),
      behavior: "smooth"
    });
  }
}

async function populateOutNow() {
  const sliders = document.querySelector(".out-now-carouselbox");
  const api_key = "d1449d341080566bedd4683998a5c14d";
  //for sample /discover/movie?
  
  var result = await axios.get(
    "https://api.themoviedb.org/3/discover/movie?api_key=" +
    api_key +
    "&primary_release_date.gte=2021-08-15&primary_release_date.lte=2021-09-22&sort_by=popularity.desc"
  );
  
  result = result.data.results;
  
  result.map(function (cur, index) {
    sliders.insertAdjacentHTML(
      "beforeend", 
      '<img class=img-'+ index + 'slider-img" src="https://image.tmdb.org/t/p/w185/' + cur.poster_path + '" />');
  });
  scrollPerClick = 400;
  console.log(result);

}

async function populateComing() {
  const sliders = document.querySelector(".coming-soon-carouselbox");
  const api_key = "d1449d341080566bedd4683998a5c14d";
  //for sample /discover/movie?
  
  var result = await axios.get(
    "https://api.themoviedb.org/3/discover/movie?api_key=" +
    api_key +
    "&primary_release_date.gte=2021-09-23&sort_by=popularity.desc"
  );
  
  result = result.data.results;
  
  result.map(function (cur, index) {
      sliders.insertAdjacentHTML(
      "beforeend", 
      '<img class=img-'+ index + 'slider-img" src="https://image.tmdb.org/t/p/w185/' + cur.poster_path + '" />');
  });
  scrollPerClick = 400;
  console.log(result);

}


//script for populating coming soon carousel with view trailer
// async function populateComing() {
//   const sliders = document.querySelector(".coming-soon-carouselbox");
//   const api_key = "d1449d341080566bedd4683998a5c14d";
//   //for sample /discover/movie?
  
//   var result = await axios.get(
//     "https://api.themoviedb.org/3/discover/movie?api_key=" +
//     api_key +
//     "&primary_release_date.gte=2021-09-23&sort_by=popularity.desc"
//   );
  
//   result = result.data.results;
  
//   result.map(function (cur, index) {
//     insert = '<div class="movie-container">\n';
//     insert += '<img class="img-' + index + 'slider-img&quot;" src="https://image.tmdb.org/t/p/w185/' + cur.poster_path + '"></img>\n';
//     insert += '<button type="button" class="view-trailer">View Trailer</button>\n</div>';

//     sliders.insertAdjacentHTML(
//       "beforeend", 
//       insert);
//   });
//   scrollPerClick = 400;
//   console.log(result);

// }


topBtn = document.getElementById("top-button");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
    topBtn.style.display = "block";
  } else {
    topBtn.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

$(document).ready(function() {
  var url;
  $('.video-btn').click(function() {
    url = $(this).data("src");
  });
  $("#myModal").on('hide.bs.modal', function() {
      $("#video").attr('src', '');
  });
  $("#myModal").on('show.bs.modal', function() {
      $("#video").attr('src', url + "?autoplay=1&amp;modestbranding=1&amp;showinfo=0");
  });
});

document.getElementById('apply').addEventListener('click', function() {
  document.getElementById('price').innerHTML = "Price: $" + document.getElementById('adultTik').value * 13.00;
})

document.getElementById('apply').addEventListener('click', function() {
  document.getElementById('price').innerHTML = "Price: $" + document.getElementById('childTik').value * 10.00;
})


//search movie 

function search() {
 
  var name = document.getElementById("searchForm").elements["searchItem"].value;
  var pattern = name.toLowerCase();
  var targetId = "";

  var divs = document.getElementsByClassName("");
  for (var i = 0; i < divs.length; i++) {
     var para = divs[i].getElementsByTagName("p");
     var index = para[0].innerText.toLowerCase().indexOf(pattern);
     if (index != -1) {
        targetId = divs[i].parentNode.id;
        document.getElementById(targetId).scrollIntoView();
        break;
     }
  }  
}
