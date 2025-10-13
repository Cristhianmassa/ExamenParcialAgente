# =====================================================
# ENTORNO ENERGÉTICO
# Configuración y validaciones básicas
# =====================================================

from dataclasses import dataclass   # para crear clases simples con menos codigo
import random                       # para valores aleatorios

# Zonas del entorno
ZV = 0  # Zona Vacía (bloqueada o impenetrable)
ZL = 1  # Zona Libre (transitable) o donde se colocan los agentes

#Diccionario para asociar zona y símbolo
SIMBOLOS = {
    ZV: "█",   # bloqueado
    ZL: "░"    # libre
}

# Características generales del entorno energético.

@dataclass
class ParamEntorno:
    N: int          # Tamaño del cubo
    Pfree: float    # % de Zonas Libres dentro del INTERIOR (no cuenta el borde)
    Psoft: float    # % de Zonas Vacías dentro del INTERIOR (no cuenta el borde)
    seed: int | None = None  # opcional, para reproducibilidad

#Validaciones
def _validar_parametros(p: ParamEntorno):
    """
    Verifica que los parámetros del entorno sean coherentes.
    """
    # N debe ser al menos 2 (para tener un volumen significativo)
    assert p.N >= 2, "N debe ser >= 2 para definir un entorno cúbico válido."

    # Los porcentajes deben estar dentro del rango permitido
    assert 0 <= p.Pfree <= 1 and 0 <= p.Psoft <= 1, "Pfree y Psoft deben estar en [0,1]."

    # La suma de Pfree y Psoft debe ser 1.0 (100% del espacio se reparte entre ambas zonas)
    suma = p.Pfree + p.Psoft
    assert abs(suma - 1.0) < 1e-9, f"Pfree + Psoft debe ser 1.0, pero es {suma}"

    # Mensaje de confirmación
    print(f"✅ Parámetros validados correctamente: N={p.N}, Pfree={p.Pfree}, Psoft={p.Psoft}")

# =====================================================
# ENTORNO ENERGÉTICO
# Crear la estructura del cubo energético
# =====================================================

def crear_cubo_vacio(N: int):
    """
    Crea una estructura tridimensional (N×N×N) donde cada celda
    representa una unidad energética del entorno.
    Inicialmente todas las celdas se marcan como ZV (Zona Vacía).
    """
    # 'ZV' o representa una zona bloqueada (0)
    cubo = []
    for x in range(N):
        capa_x = []
        for y in range(N):
            fila_y = []
            for z in range(N):
                fila_y.append(ZV)
            capa_x.append(fila_y)
        cubo.append(capa_x)

    return cubo

# =====================================================
# visualización del entorno
# =====================================================

def imprimir_capas(cubo):
    """
    Muestra el entorno por capas de profundidad (eje Z).
    Cada capa Z se imprime como una cuadrícula 2D.
    """
    N = len(cubo)
    for z in range(N):
        print(f"\nCapa Z = {z}")
        for y in range(N):
            fila = ""
            for x in range(N):
                valor = cubo[x][y][z]
                fila += SIMBOLOS[valor]  # usa el símbolo visual (█ o ░)
            print(fila)

def rellenar_cubo(cubo, p: ParamEntorno):
    """
    Asigna aleatoriamente Zonas Libres (ZL) y Zonas Vacías (ZV)
    dentro del cubo según los porcentajes definidos en los parámetros.
    """
    if p.seed is not None:
        random.seed(p.seed)  # Permite reproducir el mismo entorno

    N = p.N
    total_celdas = N ** 3

    # Cantidades de cada tipo de zona
    n_libres = int(total_celdas * p.Pfree)
    n_vacias = total_celdas - n_libres

    # Crear una lista con todos los tipos de zonas a asignar
    tipos = [ZL] * n_libres + [ZV] * n_vacias
    random.shuffle(tipos)  # Mezclar aleatoriamente

    # Asignar las zonas en el cubo
    indice = 0
    for x in range(N):
        for y in range(N):
            for z in range(N):
                cubo[x][y][z] = tipos[indice]
                indice += 1