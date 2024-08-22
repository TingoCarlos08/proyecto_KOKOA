import os
import sys
import time
import random
import pygame

# Definición de colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 51)

# Configuración del tablero y sprites
ESCALA_SPRITE = 2
POS_TABLERO_X, POS_TABLERO_Y = 30, 50
TAMANIO_CASILLA = 8 * ESCALA_SPRITE
NUM_FILAS, NUM_COLUMNAS = 31, 28

# Direcciones de movimiento
QUIETO, DERECHA, ARRIBA, IZQUIERDA, ABAJO = range(5)

marcador = 0

class Entidad:
    def __init__(self, posicion, direccion, imagenes, velocidad_mov):
        self.posicion = posicion
        self.direccion = direccion
        self.imagenes = imagenes
        self.tiempo_inicio = time.time()
        self.tiempo_actual = 0
        self.velocidad_mov = velocidad_mov

class PacMan(Entidad):
    def __init__(self):
        super().__init__(posicion=(23, 13), direccion=QUIETO,
                         imagenes=['pacman0', 'pacman1', 'pacman2'],
                         velocidad_mov=1.0 / 10)
        self.invencible = False
        self.boca_abierta = 1
        self.vidas = 3

class Fantasma(Entidad):
    def __init__(self, posicion, imagen):
        super().__init__(posicion=posicion, direccion=ARRIBA,
                         imagenes=[imagen], velocidad_mov=1.0 / 8)
        self.comido = False

class Vitamina:
    def __init__(self):
        self.posiciones = [(3, 1), (3, 26), (23, 1), (23, 26)]
        self.comida = [False] * 4
        self.tiempo_comido = [0] * 4
        self.comido_una_vez = [False] * 4
        self.imagenes = ['pepa_peq', 'pepa_med', 'pepa_gra']
        self.tamano_actual = 2

    def obtener_posicion(self, indice):
        return self.posiciones[indice]

blinky = Fantasma(posicion=(14, 11), imagen='blinky')
pinky = Fantasma(posicion=(14, 13), imagen='pinky')
inky = Fantasma(posicion=(14, 15), imagen='inky')
clyde = Fantasma(posicion=(13, 13), imagen='clyde')

vitamina = Vitamina()
pacman = PacMan()

# Mapa del juego
mapa = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o#  #.#   #.##.#   #.#  #o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###MM### ##.#     ",
    "######.## #      # ##.######",
    "#     .   #      #   .     #",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##.......  .......##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

def cargar_sonido(nombre_archivo):
    ruta = os.path.join('sonidos', f'{nombre_archivo}.wav')
    try:
        return pygame.mixer.Sound(ruta)
    except pygame.error:
        error = f"No se pudo cargar el sonido {ruta}.\n{pygame.get_error()}"
        pygame.quit()
        sys.exit(error)

def cargar_imagen(nombre_archivo):
    ruta = os.path.join('imagenes', f'{nombre_archivo}.png')
    try:
        return pygame.image.load(ruta).convert()
    except pygame.error:
        error = f"No se pudo cargar la imagen {ruta}.\n{pygame.get_error()}"
        pygame.quit()
        sys.exit(error)

def animar_vitaminas():
    vitamina.tamano_actual = (vitamina.tamano_actual + 1) % 4
    num_imagen_vitamina = (vitamina.tamano_actual if vitamina.tamano_actual != 3 else 1)
    imagen_vitamina = vitamina.imagenes[num_imagen_vitamina]

    for i in range(4):
        if not vitamina.comida[i]:
            ventana.blit(imagen_ficha[imagen_vitamina],
                         (POS_TABLERO_X + vitamina.obtener_posicion(i)[1] * TAMANIO_CASILLA,
                          POS_TABLERO_Y + vitamina.obtener_posicion(i)[0] * TAMANIO_CASILLA))

def animar_fantasma(fantasma, posicion_anterior):
    fila, columna = posicion_anterior
    ventana.blit(vacio_fantasma, (POS_TABLERO_X + columna * TAMANIO_CASILLA - 3 * ESCALA_SPRITE,
                                  POS_TABLERO_Y + fila * TAMANIO_CASILLA - 3 * ESCALA_SPRITE))

    if mapa[fila][columna] == 'M':
        ventana.blit(imagen_ficha['muro_fan'], (POS_TABLERO_X + columna * TAMANIO_CASILLA,
                                                POS_TABLERO_Y + fila * TAMANIO_CASILLA))
    elif mapa[fila][columna] == '.':
        ventana.blit(imagen_ficha['pepa_peq'], (POS_TABLERO_X + columna * TAMANIO_CASILLA,
                                                POS_TABLERO_Y + fila * TAMANIO_CASILLA))
    elif mapa[fila][columna] == 'o':
        ventana.blit(imagen_ficha['pepa_gra'], (POS_TABLERO_X + columna * TAMANIO_CASILLA,
                                                POS_TABLERO_Y + fila * TAMANIO_CASILLA))
    elif mapa[fila][columna] == ' ':
        ventana.blit(imagen_ficha['vacio'], (POS_TABLERO_X + columna * TAMANIO_CASILLA,
                                             POS_TABLERO_Y + fila * TAMANIO_CASILLA))

    fila_siguiente, columna_siguiente = fantasma.posicion
    ventana.blit(imagen_ficha[fantasma.imagenes[0]],
                 (POS_TABLERO_X + columna_siguiente * TAMANIO_CASILLA - 3 * ESCALA_SPRITE,
                  POS_TABLERO_Y + fila_siguiente * TAMANIO_CASILLA - 3 * ESCALA_SPRITE))

def generar_direccion_aleatoria(fantasma):
    direcciones_posibles = []
    if puede_moverse(fantasma, DERECHA):   direcciones_posibles.append(DERECHA)
    if puede_moverse(fantasma, ARRIBA):    direcciones_posibles.append(ARRIBA)
    if puede_moverse(fantasma, IZQUIERDA): direcciones_posibles.append(IZQUIERDA)
    if puede_moverse(fantasma, ABAJO):     direcciones_posibles.append(ABAJO)

    if len(direcciones_posibles) == 1:
        return direcciones_posibles[0]
    else:
        direccion_opuesta = {DERECHA: IZQUIERDA, ARRIBA: ABAJO, IZQUIERDA: DERECHA, ABAJO: ARRIBA}[fantasma.direccion]
        if puede_moverse(fantasma, direccion_opuesta):
            direcciones_posibles.remove(direccion_opuesta)

        return random.choice(direcciones_posibles)

def mover_fantasma(fantasma):
    fila_anterior, columna_anterior = fila_siguiente, columna_siguiente = fantasma.posicion

    fantasma.tiempo_actual = time.time()
    if (fantasma.tiempo_actual - fantasma.tiempo_inicio) > fantasma.velocidad_mov:
        fantasma.direccion = generar_direccion_aleatoria(fantasma)

        if fantasma.direccion == DERECHA and columna_anterior < NUM_COLUMNAS - 1: columna_siguiente += 1
        elif fantasma.direccion == ARRIBA and fila_anterior > 0: fila_siguiente -= 1
        elif fantasma.direccion == IZQUIERDA and columna_anterior > 0: columna_siguiente -= 1
        elif fantasma.direccion == ABAJO and fila_anterior < NUM_FILAS - 1: fila_siguiente += 1

        fantasma.posicion = (fila_siguiente, columna_siguiente)
        fantasma.tiempo_inicio = time.time()

    animar_fantasma(fantasma, (fila_anterior, columna_anterior))

def animar_pacman(posicion_anterior):
    fila, columna = posicion_anterior
    ventana.blit(vacio_pacman, (POS_TABLERO_X + columna * TAMANIO_CASILLA - 3 * ESCALA_SPRITE,
                                POS_TABLERO_Y + fila * TAMANIO_CASILLA - 3 * ESCALA_SPRITE))

    pacman.boca_abierta = (pacman.boca_abierta + 1) % 4
    num_imagen_pacman = (pacman.boca_abierta if pacman.boca_abierta != 3 else 1)
    imagen_pacman = pacman.imagenes[num_imagen_pacman]

    fila_siguiente, columna_siguiente = pacman.posicion
    ventana.blit(imagen_ficha[imagen_pacman],
                 (POS_TABLERO_X + columna_siguiente * TAMANIO_CASILLA - 3 * ESCALA_SPRITE,
                  POS_TABLERO_Y + fila_siguiente * TAMANIO_CASILLA - 3 * ESCALA_SPRITE))

def mover_pacman(direccion):
    global marcador

    fila_anterior, columna_anterior = fila_siguiente, columna_siguiente = pacman.posicion

    pacman.tiempo_actual = time.time()
    if (pacman.tiempo_actual - pacman.tiempo_inicio) > pacman.velocidad_mov:
        if direccion == DERECHA and columna_anterior < NUM_COLUMNAS - 1: columna_siguiente += 1
        elif direccion == ARRIBA and fila_anterior > 0: fila_siguiente -= 1
        elif direccion == IZQUIERDA and columna_anterior > 0: columna_siguiente -= 1
        elif direccion == ABAJO and fila_anterior < NUM_FILAS - 1: fila_siguiente += 1

        if mapa[fila_siguiente][columna_siguiente] in ' .o':  # vacío, punto, vitamina
            if mapa[fila_siguiente][columna_siguiente] == '.':  # se comió un punto
                marcador += 10
                mapa[fila_siguiente][columna_siguiente] = ' '
                if not Canal_Efectos_Sonido.get_busy():
                    Canal_Efectos_Sonido.play(sonido['eating_short'])
            elif mapa[fila_siguiente][columna_siguiente] == 'o':  # se comió una vitamina
                marcador += 50
                mapa[fila_siguiente][columna_siguiente] = ' '
                for i in range(4):
                    if vitamina.obtener_posicion(i) == (fila_siguiente, columna_siguiente):
                        vitamina.comida[i] = True
                        vitamina.comido_una_vez[i] = True
                        vitamina.tiempo_comido[i] = time.time()

            pacman.posicion = (fila_siguiente, columna_siguiente)
            pacman.direccion = direccion
            pacman.tiempo_inicio = time.time()

    animar_pacman((fila_anterior, columna_anterior))

    ventana.blit(fuente['whimsy'].render('Score:', True, BLANCO, NEGRO), (10, 10))
    ventana.blit(fuente['whimsy'].render(f'{marcador}  ', True, AMARILLO, NEGRO), (100, 10))

def puede_moverse(Entidad, direccion):
    fila, columna = Entidad.posicion
    if direccion == DERECHA and columna < NUM_COLUMNAS - 1: columna += 1
    elif direccion == ARRIBA and fila > 0: fila -= 1
    elif direccion == IZQUIERDA and columna > 0: columna -= 1
    elif direccion == ABAJO and fila < NUM_FILAS - 1: fila += 1

    if isinstance(Entidad, PacMan):
        return mapa[fila][columna] in ' .o'
    return mapa[fila][columna] in 'M .o'  # Muro fantasma, vacío, punto, vitamina

def verificar_vitaminas_comidas():
    for i, vitamina_comida in enumerate(vitamina.comido_una_vez):
        if vitamina_comida and time.time() - vitamina.tiempo_comido[i] >= 5:
            vitamina.comido_una_vez[i] = False

for i in range(NUM_FILAS):
    mapa[i] = list(mapa[i])

fantasmas = [blinky, pinky, inky, clyde]

# Inicialización de Pygame
pygame.init()
reloj = pygame.time.Clock()
ventana = pygame.display.set_mode((600, 600))
pygame.display.set_caption('P A C - M A N')

# Creación de canales de sonido
Canal_Musica_Fondo = pygame.mixer.Channel(0)
Canal_Efectos_Sonido = pygame.mixer.Channel(1)

# Configuración de la fuente
fuente = {}
fuente['whimsy'] = pygame.font.Font(os.path.join('fuentes', 'whimsytt.ttf'), 25)

# Carga de sonidos
archivos_sonidos = ['opening_song', 'eating_short', 'siren']
sonido = {archivo: cargar_sonido(archivo) for archivo in archivos_sonidos}

# Carga de imágenes
archivos_imagenes = [
    'laberinto', 'blinky', 'pinky', 'inky', 'clyde', 'muro_fan', 'pepa_peq', 'pepa_med',
    'pepa_gra', 'vacio', 'pacman0', 'pacman1', 'pacman2'
]
imagen_ficha = {archivo: cargar_imagen(archivo) for archivo in archivos_imagenes}
for archivo in imagen_ficha:
    imagen_ficha[archivo] = pygame.transform.scale2x(imagen_ficha[archivo])

vacio_fantasma = imagen_ficha['blinky'].copy()
vacio_fantasma.fill(NEGRO)
vacio_pacman = imagen_ficha['pacman0'].copy()
vacio_pacman.fill(NEGRO)

# Configuración del ícono de la ventana
icono = imagen_ficha['pacman1'].copy()
icono.set_colorkey(NEGRO)
pygame.display.set_icon(icono)

# Preparación del juego
ventana.fill(NEGRO)
ventana.blit(imagen_ficha['laberinto'], (POS_TABLERO_X, POS_TABLERO_Y))

# Estado del juego
salir_juego = False
proxima_direccion = QUIETO

# Introducción
haciendo_intro = True
duracion_intro = sonido['opening_song'].get_length()
inicio_intro = time.time()
Canal_Musica_Fondo.play(sonido['opening_song'])
mapa[12][13] = mapa[12][14] = '#'

# Bucle principal
while pacman.vidas > 0 and not salir_juego:
    verificar_vitaminas_comidas()

    if haciendo_intro:
        if (time.time() - inicio_intro) > duracion_intro:
            mapa[12][13] = mapa[12][14] = 'M'
            Canal_Musica_Fondo.play(sonido['siren'], -1)
            haciendo_intro = False

    if puede_moverse(pacman, proxima_direccion):
        mover_pacman(proxima_direccion)
    else:
        mover_pacman(pacman.direccion)

    for fantasma in fantasmas:
        mover_fantasma(fantasma)

    animar_vitaminas()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            salir_juego = True

        if event.type == pygame.KEYDOWN and not haciendo_intro:
            if event.key == pygame.K_ESCAPE:
                salir_juego = True
            if event.key == pygame.K_UP:
                proxima_direccion = ARRIBA
            if event.key == pygame.K_DOWN:
                proxima_direccion = ABAJO
            if event.key == pygame.K_LEFT:
                proxima_direccion = IZQUIERDA
            if event.key == pygame.K_RIGHT:
                proxima_direccion = DERECHA

    pygame.display.update()
    reloj.tick_busy_loop(16)

pygame.quit()
sys.exit()
