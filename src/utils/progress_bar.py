import math
import colorama
from colorama import Fore

def progress_bar(progress, total, color=Fore.WHITE, bar_length=50):
    percent = 100 * (progress / float(total))
    filled_length = int(bar_length * progress // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r" + Fore.RESET)
    if progress == total:
        print()  # Para mover el cursor a la siguiente línea después de completar


# DEMO:

# numbers = [x * 5 for x in range(2000, 3000)]
# results = []

# progress_bar(0, len(numbers))
# for i, x in enumerate(numbers):
#     results.append(math.factorial(x))
#     progress_bar(i + 1, len(numbers))
