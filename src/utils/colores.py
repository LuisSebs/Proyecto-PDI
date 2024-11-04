import random
import colorama
from colorama import Fore, Back, Style

# Colores
rojo = Fore.RED
verde = Fore.GREEN
azul = Fore.BLUE
cian = Fore.CYAN
amarillo = Fore.YELLOW
magenta = Fore.MAGENTA

blanco = Fore.WHITE
reset = Fore.RESET

# Colores claros
rojo_claro = Fore.LIGHTRED_EX
verde_claro = Fore.LIGHTGREEN_EX
azul_claro = Fore.LIGHTBLUE_EX
cian_claro = Fore.LIGHTCYAN_EX
amarillo_claro = Fore.LIGHTYELLOW_EX
magenta_claro = Fore.LIGHTMAGENTA_EX

colores = [
    azul,
    verde,
    cian,
    amarillo,
    magenta,
    rojo_claro,
    verde_claro,
    azul_claro,
    cian_claro,
    magenta_claro,
    amarillo_claro,
]

def random_color():
    return random.choice(colores)
