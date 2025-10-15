# =====================================================
# entorno.py — Mundo N×N×N y dinámica de monstruos
# =====================================================
from dataclasses import dataclass
import random

# ----- Constantes de celdas -----
ZV = 0   # Zona Vacía (bloqueo total)
ZL = 1   # Zona Libre
ROBOT = 3
MONSTRUO = 4

SIMBOLOS = {
    ZV: "█",
    ZL: "░",
    ROBOT: "R",
    MONSTRUO: "M",
}

# ----- Parámetros del entorno -----
@dataclass
class ParamEntorno:
    N: int
    Pfree: float
    Psoft: float
    Nrobot: int = 0
    Nmonstruos: int = 0
    seed: int | None = None

    # Dinámica de monstruos
    K_monstruo: int = 0      # cada cuántas iteraciones se evalúa movimiento (0=desactivado)
    p_monstruo: float = 0.0  # prob. de moverse cuando “toca” (0..1)


# ----- Validación -----
def _validar_parametros(p: ParamEntorno):
    assert p.N >= 3, "N debe ser >= 3."
    assert 0 <= p.Pfree <= 1 and 0 <= p.Psoft <= 1, "Pfree y Psoft en [0,1]."
    suma = p.Pfree + p.Psoft
    assert abs(suma - 1.0) < 1e-9, f"Pfree + Psoft debe ser 1.0, pero es {suma}"
    assert p.Nrobot >= 0 and p.Nmonstruos >= 0, "Cantidades de agentes no negativas."
    assert 0.0 <= p.p_monstruo <= 1.0, "p_monstruo en [0,1]."
    assert isinstance(p.K_monstruo, int) and p.K_monstruo >= 0, "K_monstruo entero >= 0."


# ----- Construcción y utilidades -----
def crear_cubo_vacio(N: int):
    return [[[ZL for _z in range(N)] for _y in range(N)] for _x in range(N)]

def rellenar_cubo(cubo, p: ParamEntorno):
    """Rellena aleatoriamente con ZL / ZV según Pfree/Psoft."""
    if p.seed is not None:
        random.seed(p.seed)
    N = len(cubo)
    for x in range(N):
        for y in range(N):
            for z in range(N):
                cubo[x][y][z] = ZL if random.random() < p.Pfree else ZV

def construir_entorno(p: ParamEntorno):
    _validar_parametros(p)
    cubo = crear_cubo_vacio(p.N)
    rellenar_cubo(cubo, p)
    return cubo

def es_coord_valida(N: int, x: int, y: int, z: int) -> bool:
    return 0 <= x < N and 0 <= y < N and 0 <= z < N

def vecinos_6(x: int, y: int, z: int):
    return [
        (x+1, y, z), (x-1, y, z),
        (x, y+1, z), (x, y-1, z),
        (x, y, z+1), (x, y, z-1),
    ]

def obtener_posiciones(cubo, valor: int):
    N = len(cubo)
    out = []
    for x in range(N):
        for y in range(N):
            for z in range(N):
                if cubo[x][y][z] == valor:
                    out.append((x, y, z))
    return out

def celdas_libres(cubo):
    return obtener_posiciones(cubo, ZL)

def colocar_agentes(cubo, p: ParamEntorno):
    """Coloca Nrobot y Nmonstruos en celdas ZL aleatorias (sin superposición)."""
    if p.seed is not None:
        random.seed(p.seed + 1)  # pequeño offset para distribución distinta

    libres = celdas_libres(cubo)
    random.shuffle(libres)

    necesarios = p.Nrobot + p.Nmonstruos
    if len(libres) < necesarios:
        raise ValueError("No hay suficientes Zonas Libres para colocar todos los agentes.")

    # Colocar robots
    for _ in range(p.Nrobot):
        x, y, z = libres.pop()
        cubo[x][y][z] = ROBOT

    # Colocar monstruos
    for _ in range(p.Nmonstruos):
        x, y, z = libres.pop()
        cubo[x][y][z] = MONSTRUO


# ----- Impresión -----
def imprimir_capas(cubo):
    """Imprime el cubo por capas de Z (z=0 arriba)."""
    N = len(cubo)
    for z in range(N):
        print(f"z = {z}")
        for y in range(N):
            fila = []
            for x in range(N):
                v = cubo[x][y][z]
                fila.append(SIMBOLOS.get(v, "?"))
            print(" ".join(fila))
        print()


# ----- Dinámica de monstruos -----
def mover_monstruos(cubo, p: ParamEntorno, iteracion: int):
    """
    Cada K_monstruo iteraciones, cada monstruo intenta moverse con probabilidad p_monstruo
    a una celda adyacente válida (no ZV). Si el destino tiene MONSTRUO, se fusionan (queda 1).
    *No* implementamos autosuicidio en ROBOT (pendiente de confirmación).
    """
    if p.K_monstruo <= 0 or p.p_monstruo <= 0.0:
        return
    if iteracion % p.K_monstruo != 0:
        return

    N = len(cubo)
    monstruos = obtener_posiciones(cubo, MONSTRUO)
    random.shuffle(monstruos)

    for (x, y, z) in monstruos:
        if cubo[x][y][z] != MONSTRUO:
            continue
        if random.random() >= p.p_monstruo:
            continue

        candidatos = []
        for nx, ny, nz in vecinos_6(x, y, z):
            if not es_coord_valida(N, nx, ny, nz):
                continue
            destino = cubo[nx][ny][nz]
            if destino == ZV:
                continue  # no entra a ZV
            # Permitimos ZL (mover) y MONSTRUO (fusionar). ROBOT por ahora se evita.
            if destino == ROBOT:
                continue
            candidatos.append((nx, ny, nz, destino))

        if not candidatos:
            continue

        nx, ny, nz, destino = random.choice(candidatos)

        # Deja libre su celda actual
        cubo[x][y][z] = ZL

        if destino == MONSTRUO:
            # fusión: queda un monstruo
            cubo[nx][ny][nz] = MONSTRUO
        else:
            # movimiento normal a ZL
            cubo[nx][ny][nz] = MONSTRUO


def step_entorno(cubo, p: ParamEntorno, iteracion: int):
    """Avanza el mundo una iteración (por ahora solo monstruos)."""
    mover_monstruos(cubo, p, iteracion)
