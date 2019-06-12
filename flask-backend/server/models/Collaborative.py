__author__ = "Enkusellasie Feleke"

from config import ROOT
import torch
import os
import operator

def predict(userId):
    path = os.path.join(ROOT, 'input/model.pt')
    model = torch.load(path)
    model.eval()
    x = model.getMovies(userId)
    return sorted(x.items(), key=operator.itemgetter(1),reverse=True)[0:10]