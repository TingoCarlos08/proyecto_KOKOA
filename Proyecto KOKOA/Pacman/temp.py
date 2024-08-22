import time

class Criatura:
    def __init__(self, posicion, direccion, imagenes, intervalo_movimiento):
        self.posicion = posicion
        self.direccion = direccion
        self.imagenes = imagenes
        self.tiempo_inicial = time.time()
        self.tiempo_actual = 0
        self.intervalo_movimiento = intervalo_movimiento

class PacMan(Criatura):
    def __init__(self):
        super().__init__(
            posicion=(23, 13),
            direccion=1,
            imagenes=['pacman0', 'pacman1', 'pacman2'],
            intervalo_movimiento=1.0 / 10
        )
        self.invencible = False
        self.estado_boca = 1
        self.vidas = 3

class Fantasma(Criatura):
    def __init__(self):
        super().__init__(
            posicion=(0, 0),
            direccion=1,
            imagenes=[0],
            intervalo_movimiento=1.0 / 8
        )
        self._comido = False

    def set_comido(self, comido):
        self._comido = comido

    def is_comido(self):
        return self._comido

if __name__ == '__main__':
    pacman = PacMan()
    print(pacman.posicion)

    fantasma = Fantasma()
    print(fantasma.is_comido())
