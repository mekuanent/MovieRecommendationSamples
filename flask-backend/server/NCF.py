__author__ = "Enkusellasie Feleke"

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class NCF(nn.Module):
    def __init__(self, num_users, num_items, emb_size=100, hidden_sizes=[10]):
        super(NCF, self).__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.user_emb = nn.Embedding(num_users, emb_size)
        self.item_emb = nn.Embedding(num_items, emb_size)
        self.hidden_0 = nn.Linear(emb_size * 2, hidden_sizes[0])
        self.hidden_1 = nn.Linear(hidden_sizes[0], 1)

    def forward(self, u, v):
        U = self.user_emb(u)
        V = self.item_emb(v)
        x = F.relu(torch.cat([U, V], dim=1))
        x = F.relu(self.hidden_0(x))
        x = F.relu(self.hidden_1(x))
        return x

    def calc(self, userId, itemId):
        emb = F.relu(
            torch.cat([self.user_emb(torch.LongTensor([[userId]])), self.item_emb(torch.LongTensor([[itemId]]))]))
        x = F.relu(self.hidden_0(emb.flatten()))
        x = F.relu(self.hidden_1(x))
        return x

    def getMovies(self, userId):
        ratings = {}
        for itemId in range(self.num_items):
            emb = F.relu(
                torch.cat([self.user_emb(torch.LongTensor([[userId]])), self.item_emb(torch.LongTensor([[itemId]]))]))
            x = F.relu(self.hidden_0(emb.flatten()))
            x = F.relu(self.hidden_1(x))
            ratings[itemId] = x.item()

        return ratings
