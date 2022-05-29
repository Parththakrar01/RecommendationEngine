$(document).ready(() => {
  // Here, first of all I have stored the movieId and rating given by user in movie.html on sessionStorage
  // and from that i have taken that values on index page to use it for changing the recommendation.
  // I have stored the previous movie and previos rating in separate variables to check if the code is not 
  // running again for the same movie and rating.
  let prevMovie = sessionStorage.getItem('prevMovie');
  let prevRating = sessionStorage.getItem('prevRating');
  let ratedMovie = sessionStorage.getItem('ratedMovie');
  let rating = sessionStorage.getItem('ratedScore');

  console.log(typeof (ratedMovie));
  console.log(ratedMovie);
  console.log(typeof (rating));
  console.log(rating);

  if ((ratedMovie != prevMovie) || (rating != prevRating)) {
    console.log("Rated");
    // I have used the omdb api to get the information regarding the movies using their id or name
    axios.get('http://www.omdbapi.com?i=' + ratedMovie + "&apikey=ea5a1a82")
      .then((response) => {
        let movie = response.data;
        console.log(movie.Title, rating);

        // Using ajax to update the data after user rate some movie. The code for updating the data is written
        // in a python file and so we need to create a flask server which will update the data and send the 
        // response as json.
        $.ajax({
          url: "http://localhost:3000/rateMovie",
          type: 'POST',
          dataType: 'json',
          data: ([movie.Title, rating]).toString(),
          success: function (data) {
            console.log(data);   // In this case, I only need to update the column userRatings of movies variable
            // in python and so i have just returned the name and rating of movie for checking the code
          }
        });
      });
    sessionStorage.setItem('prevMovie', ratedMovie);
    sessionStorage.setItem('prevRating', rating);
  }





  // This call will be made to obtained the title of the top 10 movies from flask server and then using that to
  // show the poster of that movies on our site
  $.ajax({
    url: "http://localhost:3000/bestMovie",
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      // console.log(data);
      $('#movies').html('<div class="myText">Recommendation based on global rating, user rating and popularity</div>');
      for (i = 0; i < data.length; i++) {
        // This function is just adding the html code for showing the image and title of top 10 movies on our
        // site
        getMovies(data[i]);
      }
    }
  });

  // This function is finding the data of the movie given and writting it in our html code
  function getMovies(searchText) {
    axios.get('http://www.omdbapi.com?s=' + searchText + "&apikey=ea5a1a82")
      .then((response) => {
        let movies = response.data.Search;
        let output = `
              <div class="col-md-4">
                <div class="well text-center">
                  <a onclick="movieSelected('${movies[0].imdbID}')" href="../movie.html"><img src="${movies[0].Poster}"></img></a>
                  <h5>${movies[0].Title}</h5>
                </div>
              </div>
            `;
        $('#movies').append(output);
      })
      .catch((err) => {
        console.log(err);
      });
  }




  // This function will called the searchByName function when user enter the name of some movie 
  // on the search bar
  $('#searchForm').on('submit', (e) => {
    let searchText = $('#searchText').val();
    searchByName(searchText);
    e.preventDefault();
  });

  // This function will make the ajax post request to the flask server to find the top 10 similar movies
  // as compared to the name entered by user
  function searchByName(searchText) {
    axios.get('http://www.omdbapi.com?s=' + searchText + "&apikey=ea5a1a82")
      .then((response) => {
        // console.log(response);
        let movies = response.data.Search;
        $.ajax({
          url: "http://localhost:3000/searchMovie",
          type: 'POST',
          dataType: 'json',
          data: movies[0].Title,
          success: function (data) {
            // console.log(data);
            $('#movies').html('<div class="myText">Recommendation based on search and movies similarity</div>');
            for (i = 0; i < data.length; i++) {
              getMovies(data[i]);
            }
          }
        });
      })
      .catch((err) => {
        console.log(err);
      });
  }
})

// This function is just used to transer the id of movie whose poster is clicker from index.js to movie.js
function movieSelected(id) {
  sessionStorage.setItem('movieId', id);
  return false;
}
