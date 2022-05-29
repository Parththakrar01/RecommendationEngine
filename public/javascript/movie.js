function getMovie() {
  let movieId = sessionStorage.getItem('movieId');
  console.log(movieId);
  // This function is making api call through the id of movie to obtain its relvant information and showing it 
  // to user.
  axios.get('http://www.omdbapi.com?i=' + movieId + "&apikey=ea5a1a82")
    .then((response) => {
      // console.log(response);
      let movie = response.data;

      let output = `
    <div class="row detail">
      <div class="col-md-4">
        <img src="${movie.Poster}" class="thumbnail">
      </div>
      <div class="col-md-8">
        <h2>${movie.Title}</h2>
        <ul class="list-group">
          <li class="list-group-item"><strong>Genre:</strong> ${movie.Genre}</li>
          <li class="list-group-item"><strong>Released:</strong> ${movie.Released}</li>
          <li class="list-group-item"><strong>Rated:</strong> ${movie.Rated}</li>
          <li class="list-group-item"><strong>IMDB Rating:</strong> ${movie.imdbRating}</li>
          <li class="list-group-item"><strong>Director:</strong> ${movie.Director}</li>
          <li class="list-group-item"><strong>Writer:</strong> ${movie.Writer}</li>
          <li class="list-group-item"><strong>Actors:</strong> ${movie.Actors}</li>
        </ul>
      </div>
    </div>
    <div class="row">
      <div class="well">
        <h3 id="plot">Plot</h3>
        ${movie.Plot}
        <hr>
      </div>
    </div>
  `;
      $('#movie').html(output);
    })
    .catch((err) => {
      console.log(err);
    });
}

$(document).ready(() => {
  // When the user submit the rating, this function will be called. If initially user didn't have selected
  // any radio button then it will show warning using alert. Otherwise, it will store the movie id and the 
  // rating given by user on sessionStorage which will be used in index.js file.
  $('#submit').on('click', (e) => {
    let movieId = sessionStorage.getItem('movieId');
    let isChecked = $("[name='rating']:checked").length > 0
    if (isChecked) {
      let rating = $("[name='rating']:checked").val()
      sessionStorage.setItem('ratedMovie', movieId.toString());
      sessionStorage.setItem('ratedScore', rating.toString());
    }
    else {
      e.preventDefault();
      alert("Please check one radio button");
    }
  })
})