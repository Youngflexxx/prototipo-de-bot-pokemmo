# vision.py
import pyautogui

def detectar_interfaz():
    """Busca el botón de 'Luchar' para saber si es nuestro turno."""
    try:
        # Se requiere la imagen 'boton_luchar.png' en la misma carpeta
        if pyautogui.locateOnScreen('boton_luchar.png', confidence=0.8):
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False