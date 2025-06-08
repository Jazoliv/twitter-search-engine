import os
import sys

ERROR_IMPORTACION = "El/los archivos a importar deben existir y ser .txt válidos"
DIRECCION_ERRONEA = "No se pudo exportar a esa dirección."
TOKENIZACION_INVALIDA = "El argumento de cantidad de tokens es inválido."
DB_INVALIDA = "Error al intentar abrir el programa."

RESULTADOS_BUSQUEDA = "Resultados de la busqueda:"
NO_ENCONTRADOS = "No se encontraron tweets."
TWEETS_ELIMINADOS = "Tweets eliminados:"
NUMERO_INVALIDO = "Numero de tweet invalido."
INPUT_INVALIDO = "Input invalido."
ATRAS = "**"
FIN = "Finalizando..."
DB_PATH = "db"
LONGITUD_TOKEN_POR_DEFECTO = 3

"""valida que el ingreso de la longitud del token sea un numero natural"""
def validar_n_minima(args):
    if len(args) > 0:
        try:
            n = int(args[0])
            if n > 0:
                return n
        except ValueError:
            pass
        print(TOKENIZACION_INVALIDA)
        return None
    return LONGITUD_TOKEN_POR_DEFECTO


def normalizacion(palabra):
    letras_normalizadas = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "ü": "u",
    }

    resultado = ""
    for carac in palabra:
        if carac.isalnum():
            carac_normalizado = letras_normalizadas.get(carac.lower(), carac.lower())
            resultado += carac_normalizado

    return resultado


class TweetDatabase:
    def __init__(self, n_minimo=LONGITUD_TOKEN_POR_DEFECTO):
        self.tweets = {}
        self.tokens_palabras = {}
        self.tokens_segmentos = {}
        self.min_longitud_token = n_minimo
        self.indice = 0

        self.tweet_a_palabras = {}
        self.tweet_a_tokens = {}

    def _tokenizacion_por_palabras(self, tweet):
        palabras_normalizadas = []
        for palabra in tweet.split():
            palabras_normalizadas.append(normalizacion(palabra))
        return palabras_normalizadas

    def _tokenizacion_por_segmentos(self, tweet):
        tokens = []
        for palabra in self._tokenizacion_por_palabras(tweet):
            for i in range(len(palabra)):
                if (len(palabra) - i) >= self.min_longitud_token:
                    for longitud in range(
                        self.min_longitud_token, len(palabra) - i + 1
                    ):
                        tokens.append(palabra[i : i + longitud])
        return tokens

    def _agregar_palabras_claves(self, tweet_text, tweet_id):
        palabras = self._tokenizacion_por_palabras(tweet_text)
        self.tweet_a_palabras[tweet_id] = set(palabras)
        for palabra in palabras:
            if palabra not in self.tokens_palabras:
                self.tokens_palabras[palabra] = set()
            self.tokens_palabras[palabra].add(tweet_id)

    def _agregar_tokens(self, tweet_text, tweet_id):
        tokens = self._tokenizacion_por_segmentos(tweet_text)
        self.tweet_a_tokens[tweet_id] = set(tokens)
        for token in tokens:
            if token not in self.tokens_segmentos:
                self.tokens_segmentos[token] = set()
            self.tokens_segmentos[token].add(tweet_id)

    def _eliminar_palabras_claves(self, tweet_id):
        if tweet_id in self.tweet_a_palabras:
            for palabra in self.tweet_a_palabras[tweet_id]:
                self.tokens_palabras[palabra].remove(tweet_id)
                if not self.tokens_palabras[palabra]:
                    del self.tokens_palabras[palabra]
            del self.tweet_a_palabras[tweet_id]

    def _eliminar_tokens(self, tweet_id):
        if tweet_id in self.tweet_a_tokens:
            for token in self.tweet_a_tokens[tweet_id]:
                self.tokens_segmentos[token].remove(tweet_id)
                if not self.tokens_segmentos[token]:
                    del self.tokens_segmentos[token]
            del self.tweet_a_tokens[tweet_id]

    def agregar_tweet(self, tweet) -> int:
        tweet_indice = self.indice
        self.tweets[tweet_indice] = tweet
        self._agregar_palabras_claves(tweet, tweet_indice)
        self._agregar_tokens(tweet, tweet_indice)
        self.indice += 1
        return tweet_indice

    def eliminar_tweet(self, id_tweet: str):
        id_tweet = int(id_tweet)
        if id_tweet in self.tweets:
            tweet = self.tweets.pop(id_tweet)
            self._eliminar_palabras_claves(id_tweet)
            self._eliminar_tokens(id_tweet)
            archivo = os.path.join(DB_PATH, f"{id_tweet}.txt")
            if os.path.exists(archivo):
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write("")
            return tweet
        return None

    def buscar_tweet(self, text: str):
        match_por_clave = {}
        claves = text.split()
        for clave in claves:
            clave = normalizacion(clave)
            if clave not in match_por_clave:
                match_por_clave[clave] = set()
            if clave in self.tokens_palabras:
                for id in self.tokens_palabras[clave]:
                    match_por_clave[clave].add(id)
            if len(clave) >= self.min_longitud_token and clave in self.tokens_segmentos:
                for id in self.tokens_segmentos[clave]:
                    match_por_clave[clave].add(id)

        lista_indices = list(match_por_clave.values())
        if not lista_indices:
            return []

        interseccion = lista_indices[0]
        for inds in lista_indices[1:]:
            interseccion = interseccion.intersection(inds)

        return list(interseccion)
        
#FUNCIONES DEL TP3
    """verificamos que las rutas existan"""
    def rutas_son_validas(self, rutas: list[str]):
        for ruta in rutas:
            if not os.path.exists(ruta):
                return False
            if os.path.isdir(ruta):
                continue
            if not ruta.lower().endswith(".txt"):
                return False
        return True
    """procesa archivos y directorios y los agrega"""
    def agregar_tweets_desde_rutas(self, rutas: list[str]):
        cantidad_agregados = 0
        for ruta in rutas:
            if os.path.isdir(ruta):
                cantidad_agregados += self._procesar_directorio(ruta)
            elif os.path.exists(ruta):
                cantidad_agregados += self._procesar_archivo(ruta)
        return cantidad_agregados
    """"verifica que el archivo exista"""
    def _procesar_archivo(self, ruta: str):
        cantidad = 0
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    tweet = linea.strip()
                    if normalizacion(tweet):
                        self.agregar_tweet(tweet)
                        cantidad += 1
        except (OSError, IOError):
            pass
        return cantidad
    """verifica que el directorio exista"""
    def _procesar_directorio(self, ruta_directorio: str):
        cantidad = 0
        try:
            nombres = os.listdir(ruta_directorio)
            for nombre in nombres:
                ruta_completa = os.path.join(ruta_directorio, nombre)
                if os.path.isdir(ruta_completa):
                    cantidad += self._procesar_directorio(ruta_completa)
                elif nombre.lower().endswith(".txt"):
                    cantidad += self._procesar_archivo(ruta_completa)
        except (FileNotFoundError, NotADirectoryError):
            pass
        return cantidad
    """copia los tweets en el nuevo archivo a exportar"""
    def copiar_tweets_a_exportar(self, ruta):
        if not ruta.lower().endswith(".txt"):
            return False

        partes = ruta.split("/")
        if len(partes) > 1:
            carpeta = "/".join(partes[:-1])
            if not os.path.exists(carpeta) or not os.path.isdir(carpeta):
                return False

        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                for id in sorted(self.tweets):
                    archivo.write(self.tweets[id] + "\n")
            return True
        except OSError:
            return False
    """guarda los tweets en la base de datos local como archivos de texto"""
    def guardar_tweets(self):
        try:
            for id_tweet in self.tweets:
                ruta = os.path.join(DB_PATH, f"{id_tweet}.txt")
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(f"{self.tweets[id_tweet]}\n")
        except Exception:
            print(DB_INVALIDA)
            sys.exit(1)
    """carga los tweets desde la base de datos local y reconstruye los índices"""
    def cargar_tweets(self):
        self.tweets = {}
        self.indice = 0
        self.tokens_palabras = {}
        self.tokens_segmentos = {}
        self.tweet_a_palabras = {}
        self.tweet_a_tokens = {}
        max_id = -1
        try:
            archivos = os.listdir(DB_PATH)
            for archivo in archivos:
                if archivo.lower().endswith(".txt"):
                    id_str = archivo[:-4]
                    if id_str.isdigit():
                        id_tweet = int(id_str)
                        ruta = os.path.join(DB_PATH, archivo)
                        with open(ruta, "r", encoding="utf-8") as f:
                            contenido = f.read().strip()
                            if contenido != "":
                                self.tweets[id_tweet] = contenido
                                self._agregar_palabras_claves(contenido, id_tweet)
                                self._agregar_tokens(contenido, id_tweet)
                        if id_tweet > max_id:
                            max_id = id_tweet
            self.indice = max_id + 1
        except Exception:
            print(DB_INVALIDA)
            sys.exit(1)


def validar_input_es_segmento_valido(input: str):
    if "-" in input:
        partes = input.split("-")
        if len(partes) != 2:
            return False
        inicio, fin = partes
        return inicio.isdigit() and fin.isdigit() and int(inicio) <= int(fin)
    return input.isdigit()


def validar_input_es_id_valido(input: str, ids_validos):
    if "-" in input:
        inicio, fin = input.split("-", 1)
        ids = range(int(inicio), int(fin) + 1)
        return all(id_tweet in ids_validos for id_tweet in ids)
    return int(input) in ids_validos


def validar_input(input, ids_validos: list[int]):
    segmentos = [seg.strip() for seg in input.split(",")]

    if not all(validar_input_es_segmento_valido(seg) for seg in segmentos):
        print(INPUT_INVALIDO)
        return None

    if not all(validar_input_es_id_valido(seg, ids_validos) for seg in segmentos):
        print(NUMERO_INVALIDO)
        return None

    indices = set()
    for segmento in segmentos:
        if "-" in segmento:
            for i in range(
                int(segmento.split("-")[0]), int(segmento.split("-")[1]) + 1
            ):
                indices.add(i)
        else:
            indices.add(int(segmento))
    return list(indices)


def obtener_tweet_para_eliminar(database: TweetDatabase):
    while True:
        busqueda = input("Ingrese el tweet a eliminar:\n>>> ")
        if busqueda == ATRAS:
            return None
        if busqueda.strip() == "" or not normalizacion(busqueda):
            print(INPUT_INVALIDO)
            continue
        resultados = database.buscar_tweet(busqueda)
        if not resultados:
            print(NO_ENCONTRADOS)
            return None
        break

    print(RESULTADOS_BUSQUEDA)
    for i in sorted(resultados):
        print(f"{i}. {database.tweets[i]}")
    return resultados


def solicitar_eliminacion(ids_validos: list[int]):
    while True:
        ids_input = input("\nIngrese los numeros de tweets a eliminar:\n>>> ")
        if ids_input == ATRAS:
            return None
        ids_input = ids_input.replace(" ", "")
        if ids_input == "":
            print(INPUT_INVALIDO)
            continue
        indices = validar_input(ids_input, ids_validos)
        if indices is not None:
            return indices
            print(INPUT_INVALIDO)


def eliminar_tweets(database: TweetDatabase, indices: list[int]):
    eliminados: list[str] = []
    for indice in indices:
        eliminados.append((indice, database.tweets[indice]))
        database.eliminar_tweet(indice)
    if eliminados:
        print(TWEETS_ELIMINADOS)
        for tid, texto in sorted(eliminados):
            print(f"{tid}. {texto}")
    return eliminados


def crear_tweet(database: TweetDatabase):
    while True:
        tweet = input("Ingrese el tweet a almacenar: \n>>> ")
        if tweet == ATRAS:
            return None
        if not normalizacion(tweet):
            print(INPUT_INVALIDO)
            continue
        break

    indice = database.agregar_tweet(tweet)
    print(f"OK {indice}")
    return indice


def input_buscar_tweet(database: TweetDatabase):
    while True:
        busqueda = input("Ingrese la/s palabra/s clave a buscar:\n>>> ")
        if busqueda == ATRAS:
            return None
        if busqueda.strip() == "" or not normalizacion(busqueda):
            print(INPUT_INVALIDO)
            continue
        break
    return busqueda


def buscar_tweet(database: TweetDatabase):
    busqueda = input_buscar_tweet(database)
    if busqueda is None:
        return

    resultado = database.buscar_tweet(busqueda)

    if resultado:
        print(f"{RESULTADOS_BUSQUEDA}\n")
        for i in resultado:
            if i in database.tweets:
                print(f"{i}. {database.tweets[i]}")
    else:
        print(NO_ENCONTRADOS)


def eliminar_tweet(database: TweetDatabase):
    while True:
        ids_validos = obtener_tweet_para_eliminar(database)
        if ids_validos is None:
            # Llamada ATRAS
            break
        eliminados = solicitar_eliminacion(ids_validos)
        if eliminados is None:
            # Llamada ATRAS
            break
        eliminar_tweets(database, eliminados)
        break

#FUNCION IMPORTAR DEL TP3
def importar_tweet(database: TweetDatabase):
    while True:
        rutas = input("Ingrese la ruta del archivo a cargar:\n>>> ").strip()
        if rutas == ATRAS:
            return
        if not rutas:
            print(ERROR_IMPORTACION)
            continue
        lista_rutas = rutas.split()
        if database.rutas_son_validas(lista_rutas):
            cantidad = database.agregar_tweets_desde_rutas(lista_rutas)
            database.guardar_tweets()
            print(f"OK {cantidad}")
            return
        print(ERROR_IMPORTACION)

#FUNCION EXPORTAR DEL TP3
def exportar_tweets(database: TweetDatabase):
    while True:
        ruta = input("Ingrese la ruta del archivo a guardar:\n>>> ")
        if ruta == ATRAS:
            return
        if database.copiar_tweets_a_exportar(ruta):
            print(f"OK {len(database.tweets)}")
            break
        print(DIRECCION_ERRONEA)

#SEPARE EL MENU DEL MAIN PORQUE EL CORRECTOR AUTOMATICO NO ME DEJABA USAR UNA FUNCION MAIN TAN LARGA
def menu(database: TweetDatabase):
    while True:
        opcion = input(
            "Selecciona una de las siguientes opciones\n\n"
            "1. Crear Tweet\n"
            "2. Buscar Tweet\n"
            "3. Eliminar Tweet\n"
            "4. Importar tweets\n"
            "5. Exportar tweets\n"
            "6. Salir\n"
            ">>> "
        )

        if opcion == "1":
            id_tweet = crear_tweet(database)
            if id_tweet is not None:
                database.guardar_tweets()
        elif opcion == "2":
            buscar_tweet(database)
        elif opcion == "3":
            id_tweet = eliminar_tweet(database)
            if id_tweet is not None:
                database.guardar_tweets()
        elif opcion == "4":
            importar_tweet(database)
            database.guardar_tweets()
        elif opcion == "5":
            exportar_tweets(database)
        elif opcion == "6":
            database.guardar_tweets()
            salir()
            break
        else:
            print(INPUT_INVALIDO)


def salir():
    print(FIN)

#CAMBIOS EN EL MAIN, IMPORTAMOS ARGS
def main(args=[]):
    if not os.path.exists(DB_PATH) or not os.path.isdir(DB_PATH):
        print(DB_INVALIDA)
        sys.exit(1)
    n_tokens = validar_n_minima(args)
    if n_tokens is None:
        return
    database = TweetDatabase(n_minimo=n_tokens)
    database.cargar_tweets()
    try:
        menu(database)
    except KeyboardInterrupt:
        database.guardar_tweets()
        print(FIN)


if __name__ == "__main__":
    main(sys.argv[1:])
