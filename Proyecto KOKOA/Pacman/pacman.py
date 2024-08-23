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
        self.posicion_original = posicion  # Guardar la posición original


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

def ventana_inicio():
    while True:
        ventana.blit(background, (0, 0))  # Mostrar la imagen de fondo
        boton_rect = boton_play.get_rect(center=(300, 400))  # Posicionar el botón en el centro
        ventana.blit(boton_play, boton_rect.topleft)  # Mostrar el botón

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Detectar clic izquierdo
                if boton_rect.collidepoint(event.pos):  # Detectar clic en el botón
                    return  # Iniciar el juego si se hace clic en el botón

        pygame.display.update()  # Actualizar la pantalla
        reloj.tick(60)  # Controlar la velocidad del bucle


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
    # Si el fantasma está en dirección "QUIETO", seleccionar una dirección inicial al azar
    if fantasma.direccion == QUIETO:
        return random.choice([DERECHA, ARRIBA, IZQUIERDA, ABAJO])

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
    global fantasmas_habilitados

    # No mover a los fantasmas si no están habilitados
    if not fantasmas_habilitados:
        return

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


def mostrar_vidas():
    ventana.fill(NEGRO, (0, 570, 600, 30))  # Limpiar la zona de las vidas
    for i in range(pacman.vidas):
        ventana.blit(imagen_ficha['pacman0'], (10 + i * 40, 570))

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
                pacman.invencible = True  # Pac-Man se vuelve invencible
                pacman.tiempo_invencible = time.time()  # Guardar el tiempo en que se vuelve invencible
                # Cambiar la imagen de los fantasmas a 'Ap'
                for fantasma in fantasmas:
                    fantasma.imagenes = ['Ap']
                    fantasma.comido = False  # Reiniciar el estado comido para permitir ser comidos nuevamente
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

# Cargar imágenes para la pantalla de inicio
background = pygame.image.load(os.path.join('imagenes', 'background.jpg')).convert()
boton_play = pygame.image.load(os.path.join('imagenes', 'boton_play.png')).convert_alpha()

# Creación de canales de sonido
Canal_Musica_Fondo = pygame.mixer.Channel(0)
Canal_Efectos_Sonido = pygame.mixer.Channel(1)

# Configuración de la fuente
fuente = {}
fuente['whimsy'] = pygame.font.Font(os.path.join('fuentes', 'whimsytt.ttf'), 25)

# Carga de sonidos
archivos_sonidos = ['opening_song', 'eating_short', 'siren', 'pac_man_dies', 'eating_ghost', 'gameover', 'intermission']
sonido = {archivo: cargar_sonido(archivo) for archivo in archivos_sonidos}



# Carga de imágenes
archivos_imagenes = [
    'laberinto', 'blinky', 'pinky', 'inky', 'clyde', 'muro_fan', 'pepa_peq', 'pepa_med',
    'pepa_gra', 'vacio', 'pacman0', 'pacman1', 'pacman2', 'Ap', 'game_over', 'boton_volver_a_jugar', 'boton_inicio'
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


# Llamar a la ventana de inicio antes de comenzar el juego
ventana_inicio()

# Una vez que el jugador presiona "Start", iniciar el juego
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

def limpiar_fantasmas():
    for fantasma in fantasmas:
        fila, columna = fantasma.posicion
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

def reiniciar_juego():
    global marcador, pacman, fantasmas, proxima_direccion, haciendo_intro, inicio_intro, fantasmas_habilitados

    # Reiniciar variables del juego
    marcador = 0
    pacman = PacMan()
    proxima_direccion = QUIETO

    # Reiniciar fantasmas y sus posiciones originales
    blinky.posicion = (14, 11)
    pinky.posicion = (14, 13)
    inky.posicion = (14, 15)
    clyde.posicion = (13, 13)

    # Asegurarse de que la dirección y el estado de los fantasmas sean los iniciales
    for fantasma in fantasmas:
        fantasma.direccion = QUIETO  # Fantasmas se mantienen quietos
        fantasma.comido = False
        fantasma.tiempo_inicio = time.time()

    fantasmas = [blinky, pinky, inky, clyde]

    # Reiniciar el mapa y las posiciones de los fantasmas
    for i in range(NUM_FILAS):
        mapa[i] = list(mapa[i])
    mapa[12][13] = mapa[12][14] = 'M'

    # Reiniciar estado de introducción
    haciendo_intro = True
    inicio_intro = time.time()
    Canal_Musica_Fondo.play(sonido['opening_song'])

    # Inicializar la bandera para controlar el movimiento de los fantasmas
    fantasmas_habilitados = False

    # Limpiar la pantalla y mostrar el mapa inicial
    ventana.fill(NEGRO)
    ventana.blit(imagen_ficha['laberinto'], (POS_TABLERO_X, POS_TABLERO_Y))
    pygame.display.update()



def mostrar_pantalla_game_over():
    # Reproducir el sonido de game over
    Canal_Musica_Fondo.stop()
    Canal_Efectos_Sonido.play(sonido['gameover'])

    # Cargar imágenes para el game over
    fondo_game_over = cargar_imagen('game_over')
    boton_volver_a_jugar = cargar_imagen('boton_volver_a_jugar')
    boton_inicio = cargar_imagen('boton_inicio')

    # Mostrar fondo de game over
    ventana.blit(fondo_game_over, (0, 0))

    # Posiciones de los botones
    pos_boton_volver_a_jugar = (ventana.get_width() // 2 - boton_volver_a_jugar.get_width() // 2, 300)
    pos_boton_inicio = (ventana.get_width() // 2 - boton_inicio.get_width() // 2, 400)

    # Mostrar botones
    ventana.blit(boton_volver_a_jugar, pos_boton_volver_a_jugar)
    ventana.blit(boton_inicio, pos_boton_inicio)

    pygame.display.update()

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Detectar clic en "Volver a jugar"
                if pos_boton_volver_a_jugar[0] <= mouse_x <= pos_boton_volver_a_jugar[0] + boton_volver_a_jugar.get_width() and \
                   pos_boton_volver_a_jugar[1] <= mouse_y <= pos_boton_volver_a_jugar[1] + boton_volver_a_jugar.get_height():
                    reiniciar_juego()
                    esperando = False

                # Detectar clic en "Inicio"
                if pos_boton_inicio[0] <= mouse_x <= pos_boton_inicio[0] + boton_inicio.get_width() and \
                   pos_boton_inicio[1] <= mouse_y <= pos_boton_inicio[1] + boton_inicio.get_height():
                    ventana_inicio()  # Volver a la pantalla de inicio
                    esperando = False

def verificar_colisiones():
    global marcador

    if pacman.invencible and time.time() - pacman.tiempo_invencible > 5:
        pacman.invencible = False
        blinky.imagenes = ['blinky']
        pinky.imagenes = ['pinky']
        inky.imagenes = ['inky']
        clyde.imagenes = ['clyde']

    for fantasma in fantasmas:
        if pacman.posicion == fantasma.posicion:
            if pacman.invencible and not fantasma.comido:
                fantasma.comido = True
                marcador += 200
                Canal_Efectos_Sonido.play(sonido['eating_ghost'])
                fantasma.posicion = fantasma.posicion_original
            elif not pacman.invencible:
                pacman.vidas -= 1
                Canal_Musica_Fondo.stop()
                sonido_muerte = cargar_sonido('pac_man_dies')
                Canal_Efectos_Sonido.play(sonido_muerte)
                pygame.time.wait(int(sonido_muerte.get_length() * 1000))

                if pacman.vidas > 0:
                    limpiar_fantasmas()
                    pacman.posicion = (23, 13)
                    pacman.direccion = QUIETO
                    for f in fantasmas:
                        f.posicion = f.posicion_original
                        f.direccion = ARRIBA
                    pygame.time.wait(2000)
                    Canal_Musica_Fondo.play(sonido['siren'], -1)
                else:
                    mostrar_pantalla_game_over()

def verificar_victoria():
    for fila in mapa:
        if '.' in fila or 'o' in fila:
            return False
    return True


def mostrar_pantalla_victoria():
    # Reproducir la música de victoria
    Canal_Musica_Fondo.stop()
    Canal_Musica_Fondo.play(sonido['intermission'])  # Reproduce la música de victoria

    # Cargar la imagen de fondo de victoria
    fondo_victoria = cargar_imagen('congrats')
    boton_volver_a_jugar = cargar_imagen('boton_volver_a_jugar')
    boton_inicio = cargar_imagen('boton_inicio')

    # Mostrar fondo de victoria
    ventana.blit(fondo_victoria, (0, 0))

    # Posiciones de los botones
    pos_boton_volver_a_jugar = (ventana.get_width() // 2 - boton_volver_a_jugar.get_width() // 2, 300)
    pos_boton_inicio = (ventana.get_width() // 2 - boton_inicio.get_width() // 2, 400)

    # Mostrar botones
    ventana.blit(boton_volver_a_jugar, pos_boton_volver_a_jugar)
    ventana.blit(boton_inicio, pos_boton_inicio)

    pygame.display.update()

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Detectar clic en "Volver a jugar"
                if pos_boton_volver_a_jugar[0] <= mouse_x <= pos_boton_volver_a_jugar[0] + boton_volver_a_jugar.get_width() and \
                   pos_boton_volver_a_jugar[1] <= mouse_y <= pos_boton_volver_a_jugar[1] + boton_volver_a_jugar.get_height():
                    reiniciar_juego()  # Reinicia el juego
                    esperando = False

                # Detectar clic en "Inicio"
                if pos_boton_inicio[0] <= mouse_x <= pos_boton_inicio[0] + boton_inicio.get_width() and \
                   pos_boton_inicio[1] <= mouse_y <= pos_boton_inicio[1] + boton_inicio.get_height():
                    ventana_inicio()  # Volver a la pantalla de inicio
                    esperando = False


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
        # Habilitar el movimiento de los fantasmas cuando Pac-Man se mueva
        fantasmas_habilitados = True
    else:
        mover_pacman(pacman.direccion)

    # Limpiar y mover los fantasmas solo si están habilitados y no estamos en la introducción
    if fantasmas_habilitados and not haciendo_intro:
        limpiar_fantasmas()
        for fantasma in fantasmas:
            mover_fantasma(fantasma)

    animar_vitaminas()

    # Verificar colisiones entre Pac-Man y los fantasmas
    verificar_colisiones()

    # Verificar si Pac-Man ha comido todas las bolitas y vitaminas
    if verificar_victoria():
        mostrar_pantalla_victoria()
        break

    # Mostrar el contador de vidas
    mostrar_vidas()

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
