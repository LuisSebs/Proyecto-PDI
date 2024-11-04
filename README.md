# Proyecto PDI: FotoMosaico

<img src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHlrejBlbWhkOWg2aGIyMzhrczhvMGk3ZXMxYmtkdDZ3dHkxNWQwaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8OlT82jKm6Ugg/giphy.gif" width="400px"/>

Proyecto final del curso de Proceso Digital de Imagenes.

# Autor: Arrieta Mancera Luis Sebastian

# Dependencias:

+ [Colorama](https://pypi.org/project/colorama/): `pip install colorama`
+ [Pillow](https://pypi.org/project/pillow/): `pip install pillow`
+ [Numpy](https://numpy.org/install/) `pip install numpy`
+ [Bintrees](https://pypi.org/project/bintrees/) `pip install bintrees`

# Ejecución:

1.- Antes que nada descarga la [biblioteca de imagenes](https://www.mediafire.com/file/g8z12ixbqi7e0m9/63000fotos.rar/file) y descomprime el archivo en el directorio `./src/imagenes` de este repositorio.

2.- Favor de instalar las dependencias necesarias. Para saber informacion sobre el programa y los parametros que acepta, ejecuta con **python** o **python3** el siguiente comando:

```bash
python3 proyecto.py --help
```

Este programa recibe los siguientes parametros:

**Parametros obligatorios**

+ imagen: ruta de la imagen de la que se quiere hacer el fotomosaico
+ salida: ruta de la imagen de salida, puedes guardarla como png o jpg

**Parametros opcionales**

+ --fm: Factor del tamaño de la imagen final, cuantas veces mas grande sera el fotomosaico.
+ --f: Factor de escalado de las subimagenes, cuantas veces mas pequeña respecto al tamaño del fotomosaico seran las imagenes.
+ --t: Numero de hilos utilizados para la creacion de la imagen, se utilizan 4 hilos por default, considera este valor dado los hilos de tu procesador.

## Ejemplos

Los siguientes comandos son ejemplos que puedes utilizar para probar el programa:

**Sin parametros opcionales**
```bash
python3 proyecto.py ./imagenes/luke-braswell.jpg ./fotomosaico.png
```

**Mi ejemplo favorito**: Crear un fotomosaico de la imagen `luke-braswell.jpg` con el nombre de salida `./fotomosaico.png`, que el fotomosaico sea `2` veces más grande de la imagen original, las subimagenes serán un `0.05%` del tamaño de la imagen final y se utilizarán `4` hilos esto hace que la imagen se genere mas rápido, mi computadora tienen 24 hilos, podría usar más pero dejaré el valor que viene por defecto para que puedas visualizar como se pasan los parámetros.
```bash
python3 proyecto.py ./imagenes/luke-braswell.jpg ./fotomosaico.png --fm 2 --f 0.005 --t 4
```

# Acerca de esta implementación

Generar el fotomosaico puede tomar tiempo. Sin embargo, se utilizó un enfoque un poco distinto al de la [blog de la morsa](https://la-morsa.blogspot.com/search?q=jim+carrey). Se decidió utilizar un diccionario ya que al ser de acceso directo, buscar se vuelve muy fácil en imagenes con el tono exacto, pero cuando no se encuentra el tono exacto en el **diccionario** se busca en un **arbol rojinegro**, esta estructura de datos nos permite mantener de manera ordenada los tonos de las imagenes (además que la busqueda es en tiempo **log n**), nos aprovechamos del criterio de python para poder ordenar tuplas, por ejemplo, python puede saber si el tono `(122,230,80)` es menor o mayor que el tono `(122,230,81)`, se supone que ordena por orden **lexicográfico**, y comparamos unicamente con el valor inmediato más pequeño y el valor inmediato más grande de un tono, en esta busqueda solo tenemos que calcular la **distancia euclideana** de dos valores. Esto en conjunto con la utilización del computo paralelo optimiza bastante el tiempo de la generación de la imagen, se pierde en espacio pero se gana en tiempo. Tampoco el espacio que utilizamos es bastante ya que unicamente guardamos el **tono** como la clave y la **ruta de la imagen** como el valor tanto en el diccionario como en el arbol binario, es decir nos estamos apoyando de dos estructuras de datos con relativamente el mismo espacio.






