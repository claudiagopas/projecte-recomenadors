from abc import ABC, abstractmethod
import csv
import numpy as np
import scipy.sparse as sp
from typing import List, Dict, Tuple, Optional, Union

# === CLASSES BASE ===
class Usuari:
    def __init__(self, user_id: int, location: str = "", age: Union[float, None] = None):
        self._id = user_id
        self._location = location
        self._age = age

    def get_id(self) -> int:
        return self._id

class Item(ABC):
    def __init__(self, item_id: Union[int, str], titol: str, categoria: str):
        self._id = item_id
        self._titol = titol
        self._categoria = categoria

    def get_id(self) -> Union[int, str]:
        return self._id

# === CLASSES ESPECÍFIQUES ===
class Llibre(Item):
    def __init__(self, item_id: str, titol: str, any_publicacio: int, autor: str, editorial: str = "Desconeguda"):
        super().__init__(item_id, titol, "Llibre")
        self._any = any_publicacio
        self._autor = autor
        self._editorial = editorial

    def get_info(self) -> str:
        return f"Autor: {self._autor}, Any: {self._any}, Editorial: {self._editorial}"

class Peli(Item):
    def __init__(self, item_id: int, titol: str, genere: str, imdb_id: int = 0, tmdb_id: int = 0):
        super().__init__(item_id, titol, "Peli")
        self._genere = genere
        self._imdb_id = imdb_id
        self._tmdb_id = tmdb_id

    def get_info(self) -> str:
        return f"Gènere: {self._genere}, IMDb: {self._imdb_id}"

# === CLASSE ABSTRACTA DADES ===
class Dades(ABC):
    def __init__(self):
        self._ratings_matrix = sp.csc_matrix((0, 0), dtype=np.float32)
        self._users: List[Usuari] = []
        self._items: List[Item] = []
        self._user_id_to_idx: Dict[int, int] = {}
        self._item_id_to_idx: Dict[Union[int, str], int] = {}
        self._metadata: Dict[str, list] = {}

    def get_usuari(self, user_id: int) -> Optional[Usuari]:
        return next((u for u in self._users if u.get_id() == user_id), None)

    def get_item(self, item_id: Union[int, str]) -> Optional[Item]:
        return next((i for i in self._items if i.get_id() == item_id), None)

    @property
    def users(self) -> List[Usuari]:
        return self._users

    @property
    def items(self) -> List[Item]:
        return self._items

    @property
    def ratings_matrix(self) -> sp.csc_matrix:
        return self._ratings_matrix

    @abstractmethod
    def carregar_usuaris(self, path: str):
        pass

    @abstractmethod
    def carregar_items(self, path: str):
        pass

    @abstractmethod
    def carregar_valoracions(self, path: str):
        pass

# === IMPLEMENTACIONS CONCRETES ===
class DadesLlibres(Dades):
    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def _carregar_csv(self, fitxer: str) -> list:
        try:
            with open(fitxer, 'r', encoding='utf-8') as f:
                return list(csv.reader(f))[1:]  # Saltar capçalera
        except Exception as e:
            print(f"Error llegint {fitxer}: {str(e)}")
            return []

    def carregar_usuaris(self, path: str):
        files = self._carregar_csv(path)
        self._users = []
        
        for idx, f in enumerate(files):
            try:
                if len(f) < 3:
                    raise ValueError("Falten camps obligatoris")
                
                user_id = int(f[0])
                location = f[1].strip()
                age = float(f[2]) if f[2].strip() else None
                
                self._users.append(Usuari(user_id, location, age))
                self._user_id_to_idx[user_id] = idx
                
            except (ValueError, IndexError) as e:
                print(f"Ignorant usuari invàlid a línia {idx+1}: {str(e)}")

    def carregar_items(self, path: str):
        files = self._carregar_csv(path)
        self._items = []
        
        for idx, f in enumerate(files):
            try:
                if len(f) < 4:  # Mínim necessari: ISBN, títol, any
                    raise ValueError("Falten camps obligatoris")
                
                isbn = f[0].strip()
                titol = f[1].strip()
                
                # Maneig especial per a l'any
                any_str = f[3].strip() if len(f) > 3 else ''
                if not any_str.isdigit() and len(f) > 4:
                    any_str = f[4].strip()  # Intentem agafar l'any de la següent columna
                    
                any_pub = int(any_str) if any_str.isdigit() else 0
                
                # Maneig de l'autor
                autor = f[2].strip() if len(f) > 2 and f[2].strip() != '' else "Desconegut"
                
                # Editorial
                editorial = f[4].strip() if len(f) > 4 and any_str.isdigit() else "Desconeguda"
                
                self._items.append(Llibre(isbn, titol, any_pub, autor, editorial))
                self._item_id_to_idx[isbn] = idx
                
            except (ValueError, IndexError) as e:
                print(f"Ignorant llibre invàlid a línia {idx+1}: {str(e)}")

    def carregar_valoracions(self, path: str):
        files = self._carregar_csv(path)
        num_users = len(self._users)
        num_items = len(self._items)
        
        rows = []
        cols = []
        data = []
        
        for f in files:
            try:
                if len(f) < 3:
                    raise ValueError("Falten camps obligatoris")
                
                user_id = int(f[0])
                isbn = f[1].strip()
                rating = float(f[2])

                # Ignorar valoracions 0 (modificació clau)
                if rating == 0:
                    continue
                
                user_idx = self._user_id_to_idx.get(user_id)
                item_idx = self._item_id_to_idx.get(isbn)
                
                if user_idx is not None and item_idx is not None:
                    rows.append(user_idx)
                    cols.append(item_idx)
                    data.append(rating)
                    
            except (ValueError, KeyError) as e:
                print(f"Valoració invàlida: {f} - {str(e)}")
        
        if rows and cols and data:
            coo = sp.coo_matrix((data, (rows, cols)), shape=(num_users, num_items), dtype=np.float32)
            self._ratings_matrix = coo.tocsc()
        else:
            self._ratings_matrix = sp.csc_matrix((num_users, num_items), dtype=np.float32)

class DadesPelis(Dades):
    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def _carregar_csv(self, fitxer: str) -> list:
        try:
            with open(fitxer, 'r', encoding='utf-8') as f:
                return list(csv.reader(f))[1:]
        except Exception as e:
            print(f"Error llegint {fitxer}: {str(e)}")
            return []

    def carregar_usuaris(self, path: str):
        files = self._carregar_csv(path)
        self._users = []
        user_ids = set()
        
        for idx, f in enumerate(files):
            try:
                if not f:
                    continue
                
                user_id = int(f[0])
                if user_id not in user_ids:
                    self._users.append(Usuari(user_id))
                    user_ids.add(user_id)
                    
            except (ValueError, IndexError) as e:
                print(f"Ignorant usuari invàlid a línia {idx+1}: {str(e)}")
        
        self._user_id_to_idx = {user.get_id(): idx for idx, user in enumerate(self._users)}

    def carregar_items(self, path: str):
        files = self._carregar_csv(path)
        self._items = []
        
        for idx, f in enumerate(files):
            try:
                if len(f) < 3:
                    raise ValueError("Falten camps obligatoris")
                
                movie_id = int(f[0])
                titol = f[1].strip()
                genere = f[2].split('|')[0].strip() if len(f) > 2 else ""
                
                self._items.append(Peli(movie_id, titol, genere))
                self._item_id_to_idx[movie_id] = idx
                
            except (ValueError, IndexError) as e:
                print(f"Ignorant pel·lícula invàlida a línia {idx+1}: {str(e)}")

    def carregar_valoracions(self, path: str):
        files = self._carregar_csv(path)
        num_users = len(self._users)
        num_items = len(self._items)
        
        rows = []
        cols = []
        data = []
        
        for f in files:
            try:
                if len(f) < 3:
                    raise ValueError("Falten camps obligatoris")
                
                user_id = int(f[0])
                movie_id = int(f[1])
                rating = float(f[2])

                # Ignorar valoracions 0 (modificació clau)
                if rating == 0:
                    continue
                
                user_idx = self._user_id_to_idx.get(user_id)
                item_idx = self._item_id_to_idx.get(movie_id)
                
                if user_idx is not None and item_idx is not None:
                    rows.append(user_idx)
                    cols.append(item_idx)
                    data.append(rating)
                    
            except (ValueError, KeyError) as e:
                print(f"Valoració invàlida: {f} - {str(e)}")
        
        if rows and cols and data:
            coo = sp.coo_matrix((data, (rows, cols)), shape=(num_users, num_items), dtype=np.float32)
            self._ratings_matrix = coo.tocsc()
        else:
            self._ratings_matrix = sp.csc_matrix((num_users, num_items), dtype=np.float32)

    def carregar_links(self, path: str):
        self._metadata['links'] = self._carregar_csv(path)

    def carregar_tags(self, path: str):
        self._metadata['tags'] = self._carregar_csv(path)

# === SISTEMA DE RECOMANACIÓ ===
class Recomanador(ABC):
    def __init__(self, dades: Dades):
        self._dades = dades

    @abstractmethod
    def recomana(self, user_id: int, n: int) -> List[Tuple[Item, float]]:
        pass

class RecomanadorSimple(Recomanador):
    def __init__(self, dades: Dades, min_vots: int = 3):
        super().__init__(dades)
        self._min_vots = min_vots

    def recomana(self, user_id: int, n: int = 5) -> List[Tuple[Item, float]]:
        usuari = self._dades.get_usuari(user_id)
        if not usuari:
            raise ValueError(f"Usuari {user_id} no trobat")
        
        user_idx = self._dades._user_id_to_idx.get(user_id)
        if user_idx is None:
            return []

        # Obtenir items valorats (ignorant 0s)
        user_ratings = self._dades.ratings_matrix.getrow(user_idx)
        items_valorats = user_ratings.indices

        # Calcular popularitat global (excloent 0s)
        total_ratings = self._dades.ratings_matrix.data
        avg_global = np.mean(total_ratings) if total_ratings.size > 0 else 0.0

        puntuacions = []
        for item_idx, item in enumerate(self._dades.items):
            if item_idx in items_valorats:
                continue
            
            # Obtenir valoracions de l'ítem (només no 0s)
            item_ratings = self._dades.ratings_matrix.getcol(item_idx)
            valid_ratings = item_ratings.data
            num_vots = valid_ratings.size
            
            if num_vots < self._min_vots:
                continue

            avg_item = np.mean(valid_ratings) if num_vots > 0 else 0.0
            
            # Fórmula de ponderació (segons PDF)
            score = (num_vots / (num_vots + self._min_vots)) * avg_item
            score += (self._min_vots / (num_vots + self._min_vots)) * avg_global
            puntuacions.append((item, score))

        puntuacions.sort(key=lambda x: x[1], reverse=True)
        return puntuacions[:n]

# === MAIN ===
def main():
    print("=== SISTEMA DE RECOMANACIÓ ===")
    tipus = input("Selecciona el tipus de dades (llibres/pelis): ").lower()
    
    if tipus == "llibres":
        dades = DadesLlibres("carpeta_books/")
        dades.carregar_usuaris("carpeta_books/Users.csv")
        dades.carregar_items("carpeta_books/Books.csv")
        dades.carregar_valoracions("carpeta_books/Ratings.csv")
    elif tipus == "pelis":
        dades = DadesPelis("carpeta_movies/")
        dades.carregar_usuaris("carpeta_movies/ratings.csv")
        dades.carregar_items("carpeta_movies/movies.csv")
        dades.carregar_valoracions("carpeta_movies/ratings.csv")
        dades.carregar_links("carpeta_movies/links.csv")
        dades.carregar_tags("carpeta_movies/tags.csv")
    else:
        print("Tipus no vàlid")
        return

    recomanador = RecomanadorSimple(dades, min_vots=3)  # min_vots=3 segons PDF

    while True:
        user_input = input("\nIntrodueix ID d'usuari (ENTER per sortir): ").strip()
        if not user_input:
            break

        try:
            user_id = int(user_input)
            recomanacions = recomanador.recomana(user_id, 5)
            
            if not recomanacions:
                print("No hi ha recomanacions disponibles")
            else:
                print(f"\nTop 5 recomanacions per {user_id}:")
                for idx, (item, puntuacio) in enumerate(recomanacions, 1):
                    print(f"{idx}. {item._titol} ({item._categoria})")
                    if isinstance(item, Llibre):
                        print(f"   {item.get_info()}")
                    elif isinstance(item, Peli):
                        print(f"   {item.get_info()}")
                    print(f"   Puntuació estimada: {puntuacio:.2f}\n")
        except ValueError:
            print("ID ha de ser un número enter")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()