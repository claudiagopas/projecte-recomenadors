#recomenador colaboratiu
import csv
import os
import numpy as np
import scipy.sparse as sp
from typing import List, Dict, Optional, Union, Tuple
from abc import ABC, abstractmethod
from .dades import Dades
from .recomanador import Recomanador



class RecomanadorCol·laboratiu(Recomanador):
    def __init__(self, dades: Dades, min_vots: int = 3):
        super().__init__(dades)
        self._min_vots = min_vots

    
    def calcula_k(user_id, matrix, k):
        n_users = len(matrix)
        similarities = {}
        
        # Obtenir les valoracions de l'usuari seleccionat
        user_ratings = matrix[user_id]
        
        # Comparar amb tots els altres usuaris
        for other_id in range(n_users):
            if other_id != user_id:
                other_ratings = matrix[other_id]
                common_items = [i for i in range(len(user_ratings)) if user_ratings[i] != 0 and other_ratings[i] != 0]
                
                if not common_items:
                    similarities[other_id] = 0
                    continue
                    
                numerator = sum(user_ratings[i] * other_ratings[i] for i in common_items)
                sum_u_sq = sum(user_ratings[i] ** 2 for i in common_items)
                sum_v_sq = sum(other_ratings[i] ** 2 for i in common_items)
                denominator = (sum_u_sq ** 0.5) * (sum_v_sq ** 0.5)
                
                if denominator == 0:
                    similarities[other_id] = 0
                else:
                    similarities[other_id] = numerator / denominator
        
        # Ordenar i agafar els k més similars
        similituds_ordenades = dict(sorted(similarities.items(), key=lambda x: x[1], reverse=True))
        return dict(list(similituds_ordenades.items())[:k])

    def recomana(user_id, matrix, k):
        # Calcular les similituds amb els k usuaris més similars
        similituds = calcula_k(user_id, matrix, k)
        
        # Calcular la mitjana de les puntuacions de l'usuari actiu (mu)
        user_ratings = matrix[user_id]
        rated_items = [i for i in range(len(user_ratings)) if user_ratings[i] != 0]
        mu = sum(user_ratings[i] for i in rated_items) / len(rated_items) if rated_items else 0
        
        # Calcular les mitjanes dels k usuaris similars
        similar_users_ratings = {uid: matrix[uid] for uid in similituds.keys()}
        mu_similar = {}
        for uid, ratings in similar_users_ratings.items():
            rated_items_similar = [i for i in range(len(ratings)) if ratings[i] != 0]
            mu_similar[uid] = sum(ratings[i] for i in rated_items_similar) / len(rated_items_similar) if rated_items_similar else 0
        
        # Calcular puntuacions predites per a tots els ítems no valorats
        predictions = {}
        for item in range(len(user_ratings)):
            if user_ratings[item] == 0:  # Només predir per ítems no valorats
                numerator = 0
                denominator = 0
                for uid, sim in similituds.items():
                    if similar_users_ratings[uid][item] != 0:
                        numerator += sim * (similar_users_ratings[uid][item] - mu_similar[uid])
                        denominator += abs(sim)
                predictions[item] = mu + (numerator / denominator if denominator != 0 else 0)
        
        # Retornar llista d'ítems ordenats per puntuació (de major a menor)
        recommended = [item for item, score in sorted(predictions.items(), key=lambda x: x[1], reverse=True)]
        return recommended

    





    