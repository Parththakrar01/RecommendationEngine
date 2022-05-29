# RecommendationEngine
This is the basic recommendation engine which works on the item-item collabarative technique. First of all, it calculate the score of the movie based on global
ratings and popularities to give us the list of top 10 movies with highest score. Now, it has the rating system where user can rate a movie on scale of 0 to 10. This 
rating will taken into account for the next time to give the top 10 movies. Movies that are more similar to the movie rated will have more change in their score
as compared to the one that are less similar. Also, There is a search bar which will search for the similar movies. For finding the similarity between two movies, I have
used the cosine similarity between two vectors. 
