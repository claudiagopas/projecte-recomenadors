from abc import ABC, abstractmethod
import csv
import numpy as np
from typing import List, Dict, Tuple, Union

# === CLASSES ESPECÍFIQUES ===
class Llibre(Item):
    def __init__(self, id: int, nom: str, any: int, autor: str):
        super().__init__(id, nom)
        self._any = any
        self._autor = autor

    def get_any(self) -> int:
        return self._any

    def get_autor(self) -> str:
        return self._autor

class Peli(Item):
    def __init__(self, id: int, nom: str, genere: str):
        super().__init__(id, nom)
        self._genere = genere

    def get_genere(self) -> str:
        return self._genere


# === MAIN ===
def main():
    print("=== INICI DEL SISTEMA DE RECOMANACIÓ ===")

    tipus_dades = input("Selecciona el tipus de dades (llibres/pelis): ").strip().lower()
    metode = input("Selecciona el mètode de recomanació (simple): ").strip().lower()

    if tipus_dades not in ["llibres", "pelis"]:
        print("Tipus de dades no vàlid.")
        return

    if metode != "simple":
        print("De moment només està implementat el mètode 'simple'.")
        return

    # Carreguem les dades segons el tipus
    if tipus_dades == "llibres":
        dades = DadesLlibres("carpeta_books/")
        dades.carregar_usuaris("carpeta_books/Users.csv")
        dades.carregar_items("carpeta_books/Books.csv")
        dades.carregar_valoracions("carpeta_books/Ratings.csv")
    else:
        dades = DadesPelis("carpeta_movies/")
        dades.carregar_usuaris("carpeta_movies/ratings.csv")
        dades.carregar_items("carpeta_movies/movies.csv")
        dades.carregar_valoracions("carpeta_movies/ratings.csv")
        dades.carregar_links("carpeta_movies/links.csv")
        dades.carregar_tags("carpeta_movies/tags.csv")

    # Inicialitzem el recomanador
    recomanador = RecomanadorSimple(dades, min_vots=3)

    while True:
        user_input = input("\nIntrodueix l'ID de l'usuari per fer recomanacions (enter per sortir): ").strip()
        if user_input == "":
            print("Finalitzant el programa.")
            break

        try:
            user_id = int(user_input)
        except ValueError:
            print("ID no vàlid. Introdueix un número d'usuari.")
            continue

        usuari = dades.get_usuari(user_id)
        if usuari is None:
            print("Usuari no trobat.")
            continue

        recoms = recomanador.recomana(user_id, n=5)
        if not recoms:
            print("No s'han trobat recomanacions per aquest usuari.")
        else:
            print(f"\nRecomanacions per a l'usuari {user_id}:")
            for item, score in recoms:
                print(f"- Títol: {item._titol}, Categoria: {item._categoria}, Puntuació: {score:.2f}")

if __name__ == "__main__":
    main()
