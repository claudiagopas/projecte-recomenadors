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

    def ordena_similituts()
    def calcula_k(user_id, matrix, item_ids):
    # Matriu on files són usuaris i columnes són pel·lícules
        n_users = len(matrix)
        similarities = {}
        
        # Obtenir les valoracions de l'usuari seleccionat
        user_ratings = dict(zip(item_ids, matrix[user_id]))
        
        # Comparar amb tots els altres usuaris
        for other_id in range(n_users):
            if other_id != user_id:  # Evitar comparar l'usuari amb si mateix
                other_ratings = dict(zip(item_ids, matrix[other_id]))
                common_items = [i for i in item_ids if user_ratings.get(i) is not None and other_ratings.get(i) is not None and user_ratings[i] != 0 and other_ratings[i] != 0]
                
                if not common_items:
                    similarities[other_id] = 0
                    continue
                    
                # Suma dels productes de les valoracions
                numerator = sum(user_ratings[i] * other_ratings[i] for i in common_items)
                
                # Sumes dels quadrats de les valoracions
                sum_u_sq = sum(user_ratings[i] ** 2 for i in common_items)
                sum_v_sq = sum(other_ratings[i] ** 2 for i in common_items)
                
                # Calcular similitud del cosinus
                denominator = (sum_u_sq ** 0.5) * (sum_v_sq ** 0.5)
                
                if denominator == 0:
                    similarities[other_id] = 0
                else:
                    similarities[other_id] = numerator / denominator
        
        return similarities

     
        def ordenar_similituts(similarities,k):
            

    def recomana(self, user_id: int, n: int = 10) -> List[Tuple[int, float]]: