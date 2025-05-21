#recomenador colaboratiu

class RecomanadorCol·laboratiu(Recomanador):
    def __init__(self, dades: Dades, min_vots: int = 3):
        super().__init__(dades)
        self._min_vots = min_vots

    def calcular_k(usua):
        # Implementar el càlcul de k (k més propers)

        pass
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