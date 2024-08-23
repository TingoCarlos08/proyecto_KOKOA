import pygame
import numpy as np


def cargar_imagen(archivo):
    nombre_archivo = archivo + '.png'
    try:
        imagen = pygame.image.load(nombre_archivo).convert()
    except pygame.error:
        texto_error = 'No se pudo cargar la imagen {0}.\n{1}'.\
            format(nombre_archivo, pygame.get_error())
        pygame.quit()
        raise SystemExit(texto_error)

    return imagen


def verificar_8x8_imagen(imagen):
    # se calcula el tamaño de la imagen
    ancho, alto = imagen.get_rect().size
    NFIL, NCOL = alto/8, ancho/8 # filas, columnas

    if NFIL != int(NFIL) or NCOL != int(NCOL):
        raise('El tamaño de la imagen no es divisible entre 8')

    return int(NFIL), int(NCOL)


pygame.init()

ventana = pygame.display.set_mode((1280, 800)) #, FULLSCREEN)

laberinto = cargar_imagen('laberinto')
NFIL, NCOL = verificar_8x8_imagen(laberinto)

pepa_peq  = cargar_imagen('pepa_peq')
pepa_gra  = cargar_imagen('pepa_gra')
muro_fan  = cargar_imagen('muro_fan')
vacio     = cargar_imagen('vacio')

surfarray_pepa_peq = pygame.surfarray.array2d(pepa_peq)
surfarray_pepa_gra = pygame.surfarray.array2d(pepa_gra)
surfarray_muro_fan = pygame.surfarray.array2d(muro_fan)
surfarray_vacio    = pygame.surfarray.array2d(vacio)

mapa = [['#' for c in range(NCOL)] for f in range(NFIL)]

esc = 3
ancho, alto = 8, 8
for f in range(NFIL):
    for c in range(NCOL):
        cuadro_8x8 = pygame.Surface((ancho, alto)).convert()
        cuadro_8x8.blit(laberinto, (0, 0), (ancho*c, alto*f, ancho, alto))

        surfarray_cuadro_8x8 = pygame.surfarray.array2d(cuadro_8x8)

        if  np.array_equal(surfarray_pepa_peq, surfarray_cuadro_8x8):
            mapa[f][c] = '.'
        elif np.array_equal(surfarray_pepa_gra, surfarray_cuadro_8x8):
            mapa[f][c] = 'o'
        elif np.array_equal(surfarray_muro_fan, surfarray_cuadro_8x8):
            mapa[f][c] = 'M'
        elif np.array_equal(surfarray_vacio, surfarray_cuadro_8x8):
            mapa[f][c] = ' '

        print(surfarray_cuadro_8x8)
        print('')

        cuadro_8x8_esc = pygame.transform.scale(cuadro_8x8, (esc*ancho, esc*alto))


        ventana.blit(cuadro_8x8_esc, (c*3*8,f*3*8))
        pygame.display.update()
f
print('NFIL =', NFIL, '   NCOL =', NCOL)
for i in range(NFIL):
    print('"' + ''.join(mapa[i]) + '",')

pygame.quit()
