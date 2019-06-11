import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)


import os
print(os.listdir("../input"))


import json

class Simple:
    def __init__(self):
        self.df1=pd.read_csv('/input/tmdb_5000_credits.csv.csv')
        self.df2=pd.read_csv('/input/tmdb_5000_movies.csv', parse_dates=True)

def preProcesser(df2=df2):
    # pre-processing (cleaning data)
    # id, popularity, budget, dropping columns imdb_id & original_title
    self.df2['id'] = pd.to_numeric(df2['id'], errors='coerce', downcast='unsigned')
    df2['id'].fillna(0, inplace=True)
    df2['id'].astype(int)

    df2['popularity'] = pd.to_numeric(df2['popularity'], errors='coerce')
    df2['popularity'].fillna(0, inplace=True)

    df2['budget'] = pd.to_numeric(df2['budget'], errors='coerce')
    df2['budget'] = df2['budget'].replace(0, np.nan)
    df2[df2['budget'].isnull()].shape

    df2 = df2.drop(['imdb_id'], axis=1)
    df2 = df2.drop('original_title', axis=1)

    df2['original_language'].drop_duplicates().shape[0]

def featureEnginner():
    # Feature-Engineering
    df2['return'] = df2['revenue'] / df2['budget']
    df2[df2['return'].isnull()].shape

    lang_df = pd.DataFrame(df2['original_language'].value_counts())
    lang_df['language'] = lang_df.index
    lang_df.columns = ['number', 'language']
    lang_df.head()

    df2 = df2.merge(df1,on='id')
    df2 = df2.merge(df3,on='id')

def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)

def getTopRatedMovies():
    # Define a new feature 'score' and calculate its value with `weighted_rating()`
    q_movies['score'] = q_movies.apply(weighted_rating, axis=1)

    #Sort movies based on score calculated above
    q_movies = q_movies.sort_values('score', ascending=False)

    #Print the top 15 movies
    q_movies[['title', 'vote_count', 'vote_average', 'score']].head(10)

    return json.dumps(json.loads(q_movies[['title', 'vote_count', 'vote_average', 'score']].head(20).to_json(orient='index')), indent=2)

def getMostPopularMovies():
    pop= df2.sort_values('popularity', ascending=False)
    return json.dumps(json.loads(df2.sort_values('popularity', ascending=False)[['title']].head(20).to_json(orient='index')), indent=2)


