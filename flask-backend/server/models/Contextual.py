import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import requests
from flask import jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity, polynomial_kernel
from sklearn import preprocessing
import json
from sklearn.preprocessing import MultiLabelBinarizer
import os.path


PROJECT_LOC = '/Users/pc/Documents/mahareshi/class/ml/projects/movie-recommender/flask-backend/server/'

INP1_LOC = PROJECT_LOC + '/input/tmdb_5000_credits.csv'
INP2_LOC = PROJECT_LOC + '/input/tmdb_5000_movies.csv'

SER2_DIR_LOC = PROJECT_LOC + '/output'
SER1_LOC = SER2_DIR_LOC + '/content_sim.npy'
SER2_LOC = SER2_DIR_LOC + '/meta_sim.npy'

class Contextual:

    def __init__(self, reconstruct=False):
        self.df1 = pd.read_csv(INP1_LOC)
        self.df2 = pd.read_csv(INP2_LOC)
        self.df1.columns = ['id', 'tittle', 'cast', 'crew']
        self.df2 = self.df2.merge(self.df1, on='id')
        self.dfc = None
        self.mlb = None
        self.cosine_sim = None
        self.meta_sim = None
        self.joined_sim = None
        self.indices = None
        self.ids = None

        if reconstruct or not (os.path.exists(SER1_LOC) and os.path.exists(SER2_LOC)):
            if not os.path.exists(SER2_DIR_LOC):
                print('please make sure, you have created output dir in the working directory!')
                exit(-1)

            self.init_data()
            self.sanitize_data()
            self.content_similarity()
            self.meta_similarity()
            self.joined_similarity()
            self.write_to_file()
        else:
            self.load_from_file()

    def init_data(self):
        self.dfc = self.df2[['title', 'genres', 'original_language', 'production_companies',
                   'release_date', 'cast']].copy()
        self.dfc['release_date'] = pd.to_datetime(self.dfc["release_date"])
        self.dfc['year'] = self.dfc['release_date'].dt.year
        self.dfc = self.dfc.drop(['release_date'], axis=1)
        self.dfc = self.dfc.rename(index=str, columns={'original_language': 'lang'})
        self.mlb = MultiLabelBinarizer()

    def convert_to_list(self, str):
        l = json.loads(str)
        arr = []
        for x in l:
            y = x['name'].replace(' ', '')
            arr.append(y)
        return arr

    def convert_to_one_hot(self, column, prefix, dfc, is_array=True):
        df_1ht = None
        if is_array:
            dfc['arr'] = dfc[column].apply(self.convert_to_list)
            X = self.mlb.fit_transform(dfc.arr)
            columns = []
            for c in self.mlb.classes_:
                columns.append(prefix + c)
            df_1ht = pd.DataFrame(X, columns=columns)
        else:
            dfc['arr'] = pd.Series(1)
            df_1ht = pd.get_dummies(dfc[column])

        dist = []
        for col in df_1ht.columns:
            dist.append([col, df_1ht[df_1ht[col] == 1].shape[0]])

        dfc.reset_index(drop=True, inplace=True)
        dfc = dfc.join(df_1ht)

        dist = pd.DataFrame(dist, columns=[column, 'count'])

        return dfc.drop([column, 'arr'], axis=1), dist

    def sanitize_data(self):
        self.dfc, dist = self.convert_to_one_hot('genres', 'gn_', self.dfc)
        self.dfc, dist = self.convert_to_one_hot('production_companies', 'pd_', self.dfc)
        self.dfc = self.dfc.drop(dist[dist['count'] < 2]['production_companies'].tolist(), axis=1)
        self.dfc, dist = self.convert_to_one_hot('cast', 'ct_', self.dfc)
        self.dfc = self.dfc.drop(dist[dist['count'] < 2]['cast'].tolist(), axis=1)
        self.dfc, dist = self.convert_to_one_hot('lang', 'lang_', self.dfc, False)
        self.dfc = self.dfc.drop(dist[dist['count'] < 2]['lang'].tolist(), axis=1)
        self.dfc['year'] = self.dfc['year'].fillna(-1)

    def content_similarity(self):
        tfidf = TfidfVectorizer(stop_words='english')
        self.df2['overview'] = self.df2['overview'].fillna('')
        tfidf_matrix = tfidf.fit_transform(self.df2['overview'])
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        self.indices = pd.Series(self.df2.index, index=self.df2['title']).drop_duplicates()
        self.ids = pd.Series(self.df2.id, index=self.df2['title']).drop_duplicates()

    def meta_similarity(self):
        csim = self.dfc.drop(['title'], axis=1).copy()
        csim = preprocessing.scale(csim)
        csim = polynomial_kernel(csim)
        self.meta_sim = csim

    def joined_similarity(self):
        self.joined_sim = (0.1 * self.meta_sim) + (0.9 * self.cosine_sim)

    # Function that takes in movie title as input and outputs most similar movies
    def get_recommendations(self, title):
        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwsie similarity scores of all movies with that movie
        sim_scores = list(enumerate(self.joined_sim[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return self.df2['title'].iloc[movie_indices]

    def write_to_file(self):
        np.save(SER1_LOC, self.cosine_sim)
        np.save(SER2_LOC, self.meta_sim)

    def load_from_file(self):
        self.cosine_sim = np.load(SER1_LOC)
        self.meta_sim = np.load(SER2_LOC)
        self.indices = pd.Series(self.df2.index, index=self.df2['title']).drop_duplicates()
        self.ids = pd.Series(self.df2.id, index=self.df2.index).drop_duplicates()
        self.joined_similarity()

    def get_rec_json(self, movies):
        results = []
        for movie in movies:
            idx, success = self.index_of(movie)
            if success:
                r = requests.get(
                    'https://api.themoviedb.org/3/movie/' + str(idx) + '?api_key=ba95c3d09bee2b2c372e524f312e7df8')
                poster = r.json()['poster_path']
                results.append({'name': movie, 'poster': poster})
        return results

    def index_of(self, title):
        try:
            return self.ids[self.indices[title]], True
        except IndexError:
            return None, False

    def get_first_movies(self, limit):
        return self.df2['title'][:limit].tolist()
