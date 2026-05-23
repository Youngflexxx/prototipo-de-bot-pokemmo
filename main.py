# main.py
import keyboard
import pydirectinput
from config import CONFIG
from controles import pausa, navegar_menu_ataques, mover_izquierda, mover_derecha
from vision import detectar_interfaz

# Estado global de los recursos
pp_actuales = CONFIG["pp_maximos"]

def ejecutar_combate():
    """Bucle interno que maneja un enfrentamiento de principio a fin."""
    global pp_actuales
    print("\n[Combate] ¡Enemigo encontrado! Iniciando secuencia...")
    
    while detectar_interfaz():
        if pp_actuales <= 0:
            print("[ALERTA] ¡Te quedaste sin PP! Deteniendo bot por seguridad.")
            return False 
            
        # 1. Atacamos
        navegar_menu_ataques(CONFIG["ataque_slot"])
        pp_actuales -= 1
        print(f"[Combate] Ataque ejecutado. PP restantes: {pp_actuales}/{CONFIG['pp_maximos']}")
        
        # 2. Espera inicial para que el menú de Lucha desaparezca al atacar
        print("[Combate] Esperando que se resuelva el turno...")
        pausa(2.5, 3.5)
        
        # 3. BUCLE DE ESPERA INTELIGENTE
        # Nos quedamos aquí hasta que vuelva el menú o el combate termine
        tiempo_espera = 0
        turno_terminado = False
        limite_timeout = 15 # Máximo de intentos (unos 15-18 segundos)
        
        while tiempo_espera < limite_timeout:
            # Si el botón vuelve a aparecer, es nuestro siguiente turno
            if detectar_interfaz():
                turno_terminado = True
                print("[Combate] El menú regresó. Siguiente turno listo.")
                break 
            
            # Si no ha aparecido, seguimos presionando cancelar para avanzar textos de XP/Daño
            pydirectinput.press(CONFIG["tecla_cancelar"])
            pausa(0.8, 1.2)
            tiempo_espera += 1
            
        # Si llegamos al límite de timeout y el menú nunca volvió, asumimos la victoria
        if not turno_terminado:
            print("[Combate] Timeout alcanzado. Combate finalizado con éxito.")
            break # Rompe el bucle principal de combate y vuelve al mapa
            
        # Pequeña pausa para estabilizar antes de que el while principal repita el ataque
        pausa(0.5, 1.0)

    print("[Combate] Volviendo al mapa.")
    return True

def iniciar():
    """Inicia el bucle principal de patrullaje."""
    print(f"Bot listo. Empezaremos con {pp_actuales} PP.")
    print("Mantén presionada 'Q' para detener el bot.")
    pausa(3.0, 3.0) 
    
    while True:
        # Kill-switch de seguridad
        if keyboard.is_pressed('q'):
            print("\n[!] Bot detenido por el usuario.")
            break
            
        # Si detectamos el menú raíz, iniciamos la máquina de estados de combate
        if detectar_interfaz():
            continuar = ejecutar_combate()
            if not continuar:
                break # Rompe el bucle si nos quedamos sin PP
        else:
            # Estado Patrullar
            mover_izquierda()
            mover_derecha()

if __name__ == "__main__":
    iniciar()