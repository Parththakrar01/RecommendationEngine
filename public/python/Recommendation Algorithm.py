from ctypes import addressof
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from flask import Flask, request
import json
import string
from scipy import spatial
from nltk.corpus import stopwords
stopwords = stopwords.words("english")

app = Flask(__name__) 




def myVectorizer(givenList, universalList):
    # This function is used to convert the list into the binary vector which stores '0' if the given element is
    # not present in the list and '1' if it is present in the list.
    # Here universalList contains elements from all the movie while the givenList contains only element from
    # the given movie.
    binaryList = []
    for x in universalList:
        if x in givenList:
            binaryList.append(1)
        else:
            binaryList.append(0)
    return binaryList




def cleanString(text):
    # This function does 3 tasks. First of all, it removes all the punctuation from the string because punctuation
    # does not have any importance for finding the similarity between two strings. Then, it convert the whole 
    # string into lowercase letter to avoid the problems that are cuased due to different case but same word. 
    # Finally, it remove the common words of the language which does not have any importance using stopwords.
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords])    
    return text




def findSimilarity(index1, index2, overviewTfidValue):
    # This function will find the similarity between two movies by using the properties of movies such as 
    # genres, cast, keywords and the overview of movie. It is calculated using the cosine of the two binary
    # vectors which we have obtained using the above myVectorizer function.
    
    # Here, the genreFlag column is flag column created by me to check if the genre column of the movie 
    # is not empty i.e. the binary vector that is stored in the genre column does not contain all the '0'
    # (it should have atleast one '1' to find similarity else similarity between two movies due to genre
    # is considered as 0)
    
    if not (movies.loc[index1, "genreFlag"] and movies.loc[index2, "genreFlag"]):
        genreSimilarity = 0
    else:
        # Here, the spatial.distance.cosine returns the distance between two vectors and in order to find
        # cosine between two vectors, we need to subtract this distance from 1.
        # So, we will get cosine between two vectors in range of -1 to 1 but, in order to get the value in 
        # the range of 0 to 2, we have to add 1 to the cosine values. Thus, the final equation is 
        # 2 minus the distance between two vectors.
        genreSimilarity = 2 - spatial.distance.cosine(movies.loc[index1, "genres"], movies.loc[index2, "genres"])     
    
    # Same procedure is followed for the cast, keywords and overview column
    if not (movies.loc[index1, "castFlag"] and movies.loc[index2, "castFlag"]):
        castSimilarity = 0
    else:
        castSimilarity = 2 - spatial.distance.cosine(movies.loc[index1, "cast"], movies.loc[index2, "cast"])
    if not (movies.loc[index1, "keywordsFlag"] and movies.loc[index2, "keywordsFlag"]):
        keywordSimilarity = 0
    else:
        keywordSimilarity = 2 - spatial.distance.cosine(movies.loc[index1, "keywords"], movies.loc[index2, "keywords"])
    if not (movies.loc[index1, "overviewFlag"] and movies.loc[index2, "overviewFlag"]):
        overviewSimilarity = 0
    else:   
        overviewSimilarity = 2 - spatial.distance.cosine(overviewTfidValue[index1], overviewTfidValue[index2]) 
    
    # Here, the sum of all the similarities will be in range of 0 to 8. In order to get the totalSimilarity
    # in range of 0 to 10, I have multiplied it with 10/8.
    totalSimilarity = 5*(genreSimilarity + castSimilarity + keywordSimilarity + overviewSimilarity)/4
    return totalSimilarity




# Main function starts from here
# Storing the relevant data of movies in variable
movies = pd.read_csv("../../Database/tmdb_5000_movies.csv")
credits = pd.read_csv("../../Database/tmdb_5000_credits.csv")
credits = credits.drop(columns="title")
movies = movies.merge(credits, left_on="id", right_on="movie_id")
# Deleting the data which is not useful for recommendations
movies = movies.drop(columns=["budget", "release_date", "revenue", "runtime", 
                            "original_title", "status", "homepage", "tagline", 
                            "movie_id", "original_language", "spoken_languages", 
                            "crew", "production_companies", "production_countries"])




# This rating table is dictionary which has the movie titles as key and the index of a particular movie 
# in the movies variable that we ave defined earlier and user rating as the value which is stored in list. 
# So, using this dictionary, we can get index and user rating of any movie
ratingTable = {}
for index in movies.index:
    movies.loc[index, "userRating"] = 0
    
    # As mentioned earlier, these flags are used to check if the given column have atleast one entry
    movies.loc[index, "genreFlag"] = 1
    movies.loc[index, "castFlag"] = 1
    movies.loc[index, "keywordsFlag"] = 1
    movies.loc[index, "overviewFlag"] = 1
    indexAndRating = []
    indexAndRating.append(index)
    indexAndRating.append(0)
    ratingTable[movies.loc[index, "title"]] = indexAndRating
    
    
    
    
# Printing the name of all the columns just for checking
# for col in movies.columns:
#     print(col)

# Total votes given to particular movie
no_of_votes = movies["vote_count"]

# Rating given to particular movie
rating = movies["vote_average"]

# avaerage of ratings of all the movies
average_rating = movies["vote_average"].mean()

# Minimum votes required to be in top movies.
# It is taken into account because movie with only one vote and rating 10 cannot be considered as 
# best movie
minimum_votes = movies["vote_count"].quantile(0.75)

# calculating the weight based on the votes given by users
movies["weight"] = (no_of_votes*rating + average_rating * minimum_votes) / (no_of_votes + minimum_votes)

# Apart from the weight, movie can also be recommended if it is popular.
# Thus, taking weight and popularity on scale of 0 to 1 and
# then calcualte the score of movie out of 10
min_max_scaler = MinMaxScaler()
normalized_movies = min_max_scaler.fit_transform(movies[["weight", "popularity"]])
normalized_movies = pd.DataFrame(normalized_movies, columns=["weight", "popularity"])

# print(normalized_movies)
movies["weight"] = normalized_movies["weight"]
movies["popularity"] = normalized_movies["popularity"]

# Here, I am giving equal importance to rating and popularity. 
movies["score"] = 5 * movies["weight"] + 5 * movies["popularity"]




# Getting genre column in the form of list    
movies["genres"] = movies["genres"].apply(json.loads)
allGenres = []         # This list will contains the genres of all the movies
for i in movies.index:
    if not movies.loc[i, "genres"]:    # checking if the genre list is empty and setting the flag accordingly
        movies.loc[i, "genreFlag"] = 0 
    givenList = movies.loc[i, "genres"]
    
    # this string will contain the name of genres of given movie separated by space
    givenGenre = ""                    
    for j in range(len(givenList)):
        if givenList[j]["name"].replace(" ", "") not in allGenres:
            allGenres.append(givenList[j]["name"].replace(" ", ""))
        if j!=0:
            givenGenre += " "
        givenGenre += (givenList[j]["name"]).replace(" ", "")
    movies.loc[i, "genres"] = givenGenre

# Converting the string to list 
movies["genres"] = movies["genres"].str.split(" ")

# Finally converting it to the binary vector using the myVectorizer function defined earlier
movies["genres"] = movies["genres"].apply(lambda x: myVectorizer(x, allGenres))
# print(movies.loc[0, "genres"])




# Getting cast column in the form of list. Same procedure is followed as the genre column
movies["cast"] = movies["cast"].apply(json.loads)
allActors = []
for i in movies.index:
    if not movies.loc[i, "cast"]:
        movies.loc[i, "castFlag"] = 0
    givenList = movies.loc[i, "cast"]
    givenActor = ""
    for j in range(min(3, len(givenList))):
        if givenList[j]["name"].replace(" ", "") not in allActors:
            allActors.append(givenList[j]["name"].replace(" ", ""))
        if j!=0:
            givenActor += " "
        givenActor += (givenList[j]["name"]).replace(" ", "")
    movies.loc[i, "cast"] = givenActor

movies["cast"] = movies["cast"].str.split(" ")
movies["cast"] = movies["cast"].apply(lambda x: myVectorizer(x, allActors))
# print(len(movies.loc[0, "cast"]))




# Getting keywords column in the form of list. Same procedure is followed as the genre column
movies["keywords"] = movies["keywords"].apply(json.loads)
allKeywords = []
for i in movies.index:
    if not movies.loc[i, "keywords"]:
        movies.loc[i, "keywordsFlag"] = 0
    givenList = movies.loc[i, "keywords"]
    givenKeyword = ""
    for j in range(len(givenList)):
        if givenList[j]["name"].replace(" ", "") not in allKeywords:
            allKeywords.append(givenList[j]["name"].replace(" ", ""))
        if j!=0:
            givenKeyword += " "
        givenKeyword += (givenList[j]["name"]).replace(" ", "")
    movies.loc[i, "keywords"] = givenKeyword

movies["keywords"] = movies["keywords"].str.split(" ")
movies["keywords"] = movies["keywords"].apply(lambda x: myVectorizer(x, allKeywords))




# Using the overview column. For overview column, we will use the python TfidVectorizer() function
# defined in the sklearn module. It will return the matrix having row equal to the number of movies and 
# column equal to the number of words in overview of all movies. Before passing it to the TfidVectorizer, 
# we will pass it to the cleanString function defined earlier to remove words without significant importance.
for index in movies.index:
    if not isinstance(movies.loc[index, "overview"], str):
        movies.loc[index, "overviewFlag"] = 0
        movies.loc[index, "overview"]= ""
    movies.loc[index, "overview"] = cleanString(movies.loc[index, "overview"])
    movies.loc[index, "overview"] = movies.loc[index, "overview"].strip()
    if movies.loc[index, "overview"] == "":
        movies.loc[index, "overviewFlag"] = 0

# print(movies.loc[0, "overview"])
overviewTfidValue = TfidfVectorizer().fit_transform(movies["overview"])
overviewTfidValue = overviewTfidValue.toarray()

totalRatedMovie = 0




# SetUp url which will update the user rating for the movies 
@app.route('/rateMovie', methods = ['POST'])
def rateMovies():
    global totalRatedMovie    # Count of total movies rated by current user
    global movies
    global ratingTable
    
    # Params store the bytes class having the list containing the name of movie and rating given by user
    # It is obtained from the index.js file using ajax
    params = request.get_data()
    params = params.decode("UTF-8")   # Converting byte class to string
    params = params.split(",")        # Converting string to list
    movieToRate = params[0]           # first index of list contain movie name
    rating = float(params[1])         # Second index contain rating given by user
    print(totalRatedMovie)    
    indexOfRatedMovie = ratingTable[movieToRate][0]
    # print("Hello")
    
    # if the user rate the same movie twice with the same score, then just return
    if rating == ratingTable[movieToRate][1]:    
        # print("nothing to do")
        return json.dumps(params)
    
    # if user rate the movie second time but with a different score, then updating the rating accordingly.
    if ratingTable[movieToRate][1] != 0:    
        totalRatedMovie -= 1
    
    for index in movies.index:
        # Here, I will not only update the rating of the given movie but also update the rating of the other 
        # movies based on the similarity between the given movie and other movies
        movies.loc[index, "similarity"] = findSimilarity(indexOfRatedMovie, index, overviewTfidValue)
        if ratingTable[movieToRate][1] != 0:
            # Subtracting the previous rating of the user for the same movie if it was rated before.
            if totalRatedMovie==0:
                movies.loc[index, "userRating"] = 0
            else:
                movies.loc[index, "userRating"] = ((totalRatedMovie+1)*movies.loc[index, "userRating"] 
                                               - movies.loc[index, "similarity"]*ratingTable[movieToRate][1]/10)/totalRatedMovie
        
        # And then adding the current rating. I am maintaining this userRating on the scale of 0 t0 10
        movies.loc[index, "userRating"] = (totalRatedMovie*movies.loc[index, "userRating"] 
                                               + movies.loc[index, "similarity"]*rating/10)/(totalRatedMovie+1)
    
    totalRatedMovie += 1
    ratingTable[movieToRate][1] = rating
    print(movies[["title", "userRating"]].head(10))
    
    return json.dumps(params)




# Setup url route which will find the top 10 movies based on global rating and user rating. The user 
# rating column has initial value 0 but it will get updated as the user rate movie on the scale of 
# 0 to 10. It will be updated using the rateMovies function defined above.
@app.route('/bestMovie', methods = ['POST'])
def findBestMovies():
    movies["globalAndUser"] = (0.3 * movies["score"] + 0.7 * movies["userRating"])
    # sorting the movies based on the global and user score
    sorted_list = movies.sort_values(by=["globalAndUser"], ascending=False)
    print(sorted_list[["title", "userRating"]].head(10))
    bestMovies = []
    for i in sorted_list["title"].head(10):
        bestMovies.append(i)
        
    response = json.dumps(bestMovies)
    return response





@app.route('/searchMovie', methods = ['POST'])
def searchSimilarMovies():
    # This function will return the top 10 similar movies when the user enter the name of movie
    # It calculate the similarity using the function findSimilarity as mentioned earlier and then sort it in 
    # descending order.
    movieToSearch = request.get_data()
    movieToSearch = movieToSearch.decode("UTF-8")
    
    indexOfSearchedMovie = ratingTable[movieToSearch][0]
    for index in movies.index:
        movies.loc[index, "similarity"] = findSimilarity(indexOfSearchedMovie, index, overviewTfidValue)

    # sorting the movies based on the global and user score
    sorted_list = movies.sort_values(by=["similarity"], ascending=False)
    # print(sorted_list[["title", "weight", "popularity", "score"]])

    similarMovies = []
    for i in sorted_list["title"].head(10):
        similarMovies.append(i)
        
    response = json.dumps(similarMovies)
    return response



if __name__ == "__main__": 
    app.run(port=3000)
