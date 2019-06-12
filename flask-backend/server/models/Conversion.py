import pandas as pd
from config import ROOT
import os


def getImdbId(movieId):
    path = os.path.join(ROOT, 'input/links.csv')
    df = pd.read_csv(path)
    matches = df[df['movieId'] == movieId]['tmdbId'].tolist()
    #print(movieId)
    if len(matches) > 0:
        #print(matches)
        return matches[0]
    else:
        return -1
