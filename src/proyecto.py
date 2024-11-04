import os
import ast
import json
import math
import random
import argparse
import numpy as np
from PIL import Image, ImageStat
from bintrees import RBTree
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.colores import random_color, verde, reset, rojo
from utils.progress_bar import progress_bar

# Ruta del banco de imagenes
RUTA_BASE = './imagenes/photos-800000'

# Ruta del directorio de imagenes
RUTA_JSON = './directorio_imagenes.json'

# Total de imagenes en el banco de imagenes
TOTAL_IMAGENES = 63162

def obtener_color_promedio(ruta_imagen):
    """
        Abre una imagen, regresa su color promedio y la ruta de la imagen
    """
    try:
        # Abrimos la imagen
        imagen = Image.open(ruta_imagen)
        array_imagen = np.array(imagen)
        promedio = np.mean(array_imagen, axis=(0, 1))
        color = tuple(int(valor) for valor in promedio)
        return color, ruta_imagen
    except Exception as e:
        print(rojo + f"Error al procesar {ruta_imagen}: {e}" + reset)
        return None

def color_promedio(imagen: Image):
    """
        Calcular el color promedio de una imagen
    """
    stat = ImageStat.Stat(imagen)
    return tuple(map(int, stat.mean[:3]))

def guardar_diccionario(diccionario: dict, ruta_salida):
    """
        Guarda un diccionario en un archivo JSON
    """
    with open(ruta_salida, 'w', encoding='utf-8') as archivo:
        json.dump(diccionario, archivo, ensure_ascii=False, indent=4)

def procesa_imagenes(num_hilos=4):
    """
        Procesa las imagenes del banco de imagenes calculando su color promedio y todas las posibles imagenes que tienen ese color promedio en una lista, al final guarda la informacion en un archivo JSON
    """
    imagenes = {}
    imagenes_procesadas = 0
    ultimo_porcentaje_mostrado = 0
    color = random_color()
    # Obtener la lista de archivos
    lista_archivos = [os.path.join(RUTA_BASE, nombre_archivo) for nombre_archivo in os.listdir(RUTA_BASE)]
    # Usar ThreadPoolExecutor para procesar las imágenes en paralelo con un número especificado de hilos
    with ThreadPoolExecutor(max_workers=num_hilos) as executor:
        futures = {executor.submit(obtener_color_promedio, ruta): ruta for ruta in lista_archivos}
        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                color_promedio, nombre_archivo = resultado
                clave_color_promedio = str(color_promedio)
                if clave_color_promedio in imagenes:
                    imagenes[clave_color_promedio].append(os.path.basename(nombre_archivo))
                else:
                    imagenes[clave_color_promedio] = [os.path.basename(nombre_archivo)]
                # Actualizar la barra de progreso
                imagenes_procesadas += 1
                porcentaje_actual = (imagenes_procesadas / TOTAL_IMAGENES) * 100
                if porcentaje_actual - ultimo_porcentaje_mostrado >= 1:
                    progress_bar(imagenes_procesadas, TOTAL_IMAGENES, color)
                    ultimo_porcentaje_mostrado = porcentaje_actual
                    color = random_color()
    # Guardamos el diccionario en un archivo JSON
    guardar_diccionario(imagenes, RUTA_JSON)
    # Mostramos el último progreso
    progress_bar(imagenes_procesadas, TOTAL_IMAGENES, color)
    print(verde + f"Se terminaron de procesar las imagenes ʕ•ᴥ•ʔ" + reset)

def cargar_directorio_imagenes():
    """
        Carga el directorio de imagenes en un diccionario y lo regresa.
    """
    diccionario = None
    with open(RUTA_JSON, 'r', encoding='utf-8') as archivo:
        diccionario = json.load(archivo)
    return diccionario

def arbol_rojinegro(diccionario:dict):
    """
        Organiza los valores del diccionario en un arbol rojinegro y lo regresa, esto se hace para que se puedan realizar rapido las busquedas a los tonos mas cercanos de la imagen
    """
    arbol = RBTree()
    for clave, valor in diccionario.items():
        arbol.insert(ast.literal_eval(clave), valor)
    return arbol

def escalar(imagen: Image, factor: float):
    """
        Escala una imagen dado un factor, por ejemplo 0.02 escala una imagen a un 2%
    """
    ancho_original, alto_original = imagen.size
    nuevo_ancho = int(ancho_original * factor)
    nuevo_alto = int((nuevo_ancho / ancho_original) * alto_original)
    imagen_reescalada = imagen.resize((nuevo_ancho, nuevo_alto))
    return imagen_reescalada

def distancia_euclidiana(punto1, punto2):
    """
        Obtenemos la distancia euclideana entre dos puntos
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(punto1, punto2)))

def get_imagen(tono: tuple, diccionario: dict, arbol: RBTree):
    """
        Regresa la imagen con el color promedio mas cercano o el exacto.

        Parameters :
        ------------

            tono:
                tono a buscar, por ejemplo: (174,90,252).
            
            diccionario:
                diccionario con las rutas de las imagenes (la clave es el tono en string y el valor son las rutas de las imagenes con ese tono).

            arbol:
                arbol rojinegro donde estan ordenadas las imagenes por su tono (la clave es el tono y el valor son las rutas de las imagenes con ese tono).

        Returns :
        ---------

            Pillow Image, la imagen con el tono mas cercano, es decir la imagen mas adecuada.
    """
    ruta = None
    # Si ya tenemos alguna imagen con el tono exacto
    if str(tono) in diccionario:
        # Regresamos una imagen al azar de las opciones
        ruta = random.choice(diccionario[str(tono)])
    else:
        # En caso contrario regresamos la que más se acerque al color
        piso, techo = None, None
        try:
            # Intentamos obtener el piso
            piso = arbol.floor_key(tono)
        except KeyError:
            pass
        try:
            # Intentamos obtener el techo
            techo = arbol.ceiling_key(tono)
        except KeyError:
            pass
        # Puede darse el caso en el que no haya piso (la imagen con el tono mas pequeño)
        if piso is None:
            clave_mas_cercana = techo
        # Puede darse el caso en el que no haya techo (la imagen con el tono mas grande)
        elif techo is None:
            clave_mas_cercana = piso
        # Calculamos la distancia euclideana al piso
        distancia_piso = None if not piso else distancia_euclidiana(tono, piso)
        # Calculamos la distancia euclideana al techo
        distancia_techo = None if not techo else distancia_euclidiana(tono, techo)
        # Obtenemos la clave mas cercana
        clave_mas_cercana = None
        # Recordemos que puede que no haya techo (pero no puede darse el caso en el que no haya ni techo ni piso, a fuerza debe haber alguno de los dos)
        if distancia_piso is None:
            clave_mas_cercana = techo
        # Recordemos que puede que no haya piso (pero no puede darse el caso en el que no haya ni techo ni piso, a fuerza debe haber alguno de los dos)
        elif distancia_techo is None:
            clave_mas_cercana = piso
        else:
            # Obtenemos el mas cercano
            clave_mas_cercana = piso if distancia_piso <= distancia_techo else techo
        # Regresamos la ruta a la imagen mas cercana
        ruta = random.choice(arbol.get(clave_mas_cercana))
    # Cargamos la imagen mas adecuada
    imagen_adecuada = Image.open(os.path.join(RUTA_BASE,ruta))
    return imagen_adecuada

def crear_fotomosaico(imagen: Image, factor_medida=2, f=0.02, num_hilos=4):
    """
        Crea un fotomosaico.

        Parameters :
        ------------

            imagen:
                imagen de la que se quiere hacer el fotomosaico.
            
            factor_medida:
                tamaño de la imagen final, por ejemplo si se pasa un 2 entonces la imagen será 2 veces más grande, si se pasa un 1 conservara su tamaño.
            
            f:
                tamaño de las subimagenes, por defecto el tamaño de las subimagenes será un 2% de la imagen final (esto considerando el factor_medida).
            
            num_hilos:
                numero de hilos utilizados para la creacion de la imagen, por defecto se utilizan 4, considera este parametro en base al numero de hilos de tu procesador.

        Returns :
        ---------

            fotomosaico
    """
    print(verde+'Espere un momento por favor...'+reset)
    # Cargamos nuestras estructuras de datos para buscar las imagenes
    diccionario = cargar_directorio_imagenes()
    arbol = arbol_rojinegro(diccionario)
    # Imagen aumentada
    imagen_aumentada = escalar(imagen, factor_medida)
    # Imagen reducida
    imagen_reducida = escalar(imagen_aumentada, f)
    # Dimensiones de la subimagen
    sub_ancho, sub_alto = imagen_reducida.size
    # Dimensiones de la imagen final
    ancho, alto = imagen_aumentada.size
    # Crear una imagen en blanco para colocar los bloques
    fotomosaico = Image.new('RGB', (ancho, alto))
    # Calcular el número total de bloques
    total_bloques_x = ancho // sub_ancho
    total_bloques_y = alto // sub_alto
    total_bloques = total_bloques_x * total_bloques_y
    # Inicializar contador de bloques procesados
    bloques_procesados = 0
    ultimo_porcentaje_mostrado = 0
    # Colores randoms
    color = random_color()
    # Funcion para procesar un bloque de la imagen
    def procesar_bloque(x, y):
        try:
            # Obtenemos el area de la imagen a procesar
            area = (x, y, x + sub_ancho, y + sub_alto)
            # Extraemos el area
            bloque = imagen_aumentada.crop(area)
            # Obtenemos el color promedio
            tono = color_promedio(bloque)
            # Obtenemos la imagen mas adecuada
            imagen_adecuada = get_imagen(tono, diccionario, arbol)
            # Regimencionamos la imagen
            imagen_redimensionada = imagen_adecuada.resize((sub_ancho, sub_alto))
            # Pegamos en el fotomosaico
            fotomosaico.paste(imagen_redimensionada, (x, y))
            return True
        except Exception as e:
            print(rojo + f"Error al procesar el bloque en ({x}, {y}): {e}" + reset)
            return False
    # Utilizamos un pool de hilos
    with ThreadPoolExecutor(max_workers=num_hilos) as executor:
        futures = []
        for x in range(0, ancho, sub_ancho):
            for y in range(0, alto, sub_alto):
                futures.append(executor.submit(procesar_bloque, x, y))

        for future in as_completed(futures):
            if future.result():
                # Actualizamos la barra de progreso y la mostramos
                bloques_procesados += 1
                porcentaje_actual = (bloques_procesados / total_bloques) * 100
                if porcentaje_actual - ultimo_porcentaje_mostrado >= 1:
                    progress_bar(bloques_procesados, total_bloques, color)
                    ultimo_porcentaje_mostrado = porcentaje_actual
                    color = random_color()

    # Mostramos el último progreso
    progress_bar(bloques_procesados, total_bloques, color)
    print(verde + f"Fotomosaico terminado ʕ•ᴥ•ʔ" + reset)

    return fotomosaico

if __name__ == '__main__':
    # Informacion del programa
    parser = argparse.ArgumentParser(description="Programa para crear fotomosaicos")
    # Argumentos no opcionales
    parser.add_argument("imagen", help="Ruta de la imagen de entrada")
    parser.add_argument("salida", help="Ruta de la imagen de salida")
    # Argumentos opcionales
    parser.add_argument("--fm", type=float, default=2, help="Factor del tamaño para la imagen final, por default se crea una imagen 2 veces mas grande")
    parser.add_argument("--f", type=float, default=0.02, help="Factor de escalado de las subimagenes, esta es referente al valor de --fm")
    parser.add_argument("--t", type=float, default=4, help="Numero de hilos utilizados para la creacion de la imagen, se utilizan 4 hilos por default, considera este valor dado los hilos de tu procesador")
    # Obtenemos los argumentos
    args = parser.parse_args()
    # Cargamos la imagen
    imagen = None
    try:
        imagen = Image.open(args.imagen)
    except Exception as e:
        print(rojo+f"Error al cargar la imagen: {e}"+reset)
        exit()
    # Creamos el fotomosaico y salvamos la imagen
    crear_fotomosaico(
        imagen=imagen,
        factor_medida=args.fm,
        f=args.f,
        num_hilos=args.t
    ).save(args.salida)
