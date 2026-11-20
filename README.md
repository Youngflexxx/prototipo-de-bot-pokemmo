# 🎮 PokéMMO Bot (Prototipo)

Prototipo de bot de automatización para [PokéMMO](https://pokemmo.com/) que patrulla el mapa, detecta encuentros por visión artificial y gestiona los combates de forma autónoma, con lógica anti-detección basada en timings humanos.

> ⚠️ **Aviso**: usar bots puede violar los Términos de Servicio de PokéMMO y resultar en la suspensión de tu cuenta. Úsalo bajo tu propia responsabilidad y solo en entornos de prueba.

## ✨ Características

- **Máquina de estados** (`PATROL` → `COMBAT` → `LOW_PP` → `STOPPED`) que maneja el ciclo completo del bot.
- **Detección de combates por visión artificial**: template matching con OpenCV (`assets/boton_luchar.png`) para reconocer el botón de *Luchar* en pantalla.
- **Sistema anti-detección** configurable:
  - Pausas con distribución gaussiana (timings no robóticos).
  - Micro-movimientos y patrones de caminata variables (evita caminar siempre en la misma dirección).
  - Pausas aleatorias tipo AFK y titubeos antes de atacar.
  - Jitter en el umbral de confianza de la visión artificial.
  - Uso ocasional de un slot de ataque diferente al configurado.
- **Kill-switch de seguridad**: pulsa `Q` en cualquier momento para detener el bot.
- **Control de PP**: el bot se detiene automáticamente al quedarse sin PP.
- **Configuración en YAML** (`config.yaml`) con valores por defecto en el código.

## 📁 Estructura del proyecto

```
├── main.py                  # Script original (prototipo inicial)
├── config.py                # Config del script original
├── controles.py             # Controles del script original
├── vision.py                # Visión del script original
├── config.yaml              # Configuración del paquete pokemmo_bot
├── assets/
│   └── boton_luchar.png     # Imagen de referencia para detección
├── src/pokemmo_bot/         # Paquete principal
│   ├── bot.py               # Máquina de estados principal
│   ├── anticheat.py         # Lógica de timings y patrones anti-detección
│   ├── config.py            # Dataclasses + carga de config.yaml
│   ├── controls.py          # Envío de teclas y pausas humanas
│   └── vision.py            # Detección del menú de combate
├── tests/                   # Suite de tests (pytest)
├── pyproject.toml           # Metadatos, dependencias y tooling
└── requirements.txt         # Dependencias mínimas
```

## 🛠️ Requisitos

- Python **3.11+** (probado con 3.14)
- Windows (usa `pydirectinput`, que depende de DirectInput)
- PokéMMO ejecutándose en **1920×1080** en modo ventana o pantalla completa (la imagen de referencia debe coincidir con tu interfaz)

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Youngflexxx/prototipo-de-bot-pokemmo.git
cd prototipo-de-bot-pokemmo

# Crear entorno virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate        # Windows

# Instalar dependencias
pip install -r requirements.txt

# O instalar como paquete (opcional, habilita el comando pokemmo-bot)
pip install -e .
```

## ⚙️ Configuración

Edita `config.yaml`:

```yaml
attack_slot: 3          # Slot de ataque: 1 (Arriba-Izq), 2 (Arriba-Der), 3 (Abajo-Izq), 4 (Abajo-Der)
pp_max: 25              # PP máximos del ataque elegido
vision_confidence: 0.8  # Confianza del template matching (0.0-1.0)
combat_timeout: 15      # Iteraciones máximas esperando el siguiente turno
```

Los bloques `keys` y `anti_detect` permiten ajustar teclas y el comportamiento anti-detección (pausas, probabilidad de AFK, titubeos, etc.).

## 🚀 Uso

```bash
# Opción 1: script original (prototipo)
python main.py

# Opción 2: paquete instalado
pokemmo-bot

# Opción 3: módulo de Python
python -m pokemmo_bot

# Con un archivo de config personalizado
python -m pokemmo_bot mi_config.yaml
```

1. Abre PokéMMO y colócate en una zona con encuentros salvajes.
2. Ejecuta el bot; tiene 3 segundos de espera antes de empezar.
3. Mantén presionada **`Q`** para detener el bot en cualquier momento (o `Ctrl+C`).

## 🧪 Tests y calidad de código

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Tests
pytest

# Lint
ruff check .

# Type checking
mypy src/
```

## 📦 Cómo subir cambios a GitHub

```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin main
```

## 📄 Licencia

MIT — ver `pyproject.toml`.
