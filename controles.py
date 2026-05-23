# controles.py
import time
import random
import pydirectinput
from config import CONFIG

def pausa(min_seg, max_seg):
    """Genera una pausa aleatoria para simular humanidad."""
    time.sleep(random.uniform(min_seg, max_seg))

def navegar_menu_ataques(slot):
    """Navega la cuadrícula de ataques basándose en el slot elegido."""
    print(f"[Sistema] Seleccionando ataque en el slot {slot}...")
    
    pydirectinput.press(CONFIG["tecla_accion"])
    pausa(0.5, 0.8)
    
    if slot == 2:
        pydirectinput.press(CONFIG["tecla_der"])
    elif slot == 3:
        pydirectinput.press(CONFIG["tecla_abajo"])
    elif slot == 4:
        pydirectinput.press(CONFIG["tecla_der"])
        pausa(0.1, 0.2)
        pydirectinput.press(CONFIG["tecla_abajo"])
        
    pausa(0.2, 0.4)
    pydirectinput.press(CONFIG["tecla_accion"])

def mover_izquierda():
    """Ejecuta el movimiento hacia la izquierda."""
    pydirectinput.keyDown(CONFIG["tecla_izq"])
    pausa(0.5, 0.8)
    pydirectinput.keyUp(CONFIG["tecla_izq"])

def mover_derecha():
    """Ejecuta el movimiento hacia la derecha."""
    pydirectinput.keyDown(CONFIG["tecla_der"])
    pausa(0.5, 0.8)
    pydirectinput.keyUp(CONFIG["tecla_der"])
    
def spamear_cancelar(veces=4):
    """Envía la tecla de cancelar repetidamente para saltar textos."""
    for _ in range(veces):
        pydirectinput.press(CONFIG["tecla_cancelar"])
        pausa(0.3, 0.5)