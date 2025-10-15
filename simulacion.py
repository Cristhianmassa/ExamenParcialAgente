# =====================================================
# simulacion.py — orquestación de la simulación
# =====================================================
from typing import Tuple, List
import csv
from pathlib import Path

from entorno import (
    ParamEntorno, construir_entorno, colocar_agentes,
    obtener_posiciones, imprimir_capas, step_entorno,
    ROBOT, MONSTRUO
)
from agente import Robot


def exportar_memoria_robot(robot: Robot, carpeta: str = "memorias") -> str:
    """
    Guarda la memoria episódica del robot en CSV: memorias/robot_x_y_z.csv
    Columnas: t, regla, accion, frontal_estado, percepcion, pos_pre, ori_pre, pos_post, ori_post, kills
    """
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    nombre = f"robot_{robot.x}_{robot.y}_{robot.z}.csv"
    ruta = Path(carpeta) / nombre
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "t", "regla", "accion", "frontal_estado", "percepcion",
            "pos_pre", "ori_pre", "pos_post", "ori_post", "kills"
        ])
        for row in robot.memoria:
            w.writerow([
                row.get("t"),
                row.get("regla"),
                row.get("accion"),
                row.get("frontal_estado"),
                row.get("percepcion"),
                row.get("pos_pre"),
                row.get("ori_pre"),
                row.get("pos_post"),
                row.get("ori_post"),
                row.get("kills"),
            ])
    return str(ruta)


def snapshot_estado(cubo) -> tuple:
    """
    “Huella” inmutable del estado para detectar estasis:
    posiciones de robots y monstruos (ordenadas).
    """
    robots_pos = tuple(sorted(obtener_posiciones(cubo, ROBOT)))
    mons_pos = tuple(sorted(obtener_posiciones(cubo, MONSTRUO)))
    return (robots_pos, mons_pos)


def simular(
    params: ParamEntorno,
    T_MAX: int = 200,
    verbose: bool = True,
    S_ESTASIS: int = 20
) -> Tuple[list, List[Robot]]:
    """
    Ejecuta la simulación por hasta T_MAX ticks (1 tick = 1 segundo) o hasta que
    se cumpla una condición de parada:
      - sin robots vivos
      - sin monstruos
      - estasis (S_ESTASIS ticks sin cambios relevantes)
    Devuelve (cubo, robots_vivos).
    """

    # 1) Construir mundo y poblar
    cubo = construir_entorno(params)
    colocar_agentes(cubo, params)

    # 2) Instanciar Robots desde el cubo
    robots: List[Robot] = [
        Robot(x, y, z, orientacion="X+")
        for (x, y, z) in obtener_posiciones(cubo, ROBOT)
    ]

    def contar_monstruos() -> int:
        return len(obtener_posiciones(cubo, MONSTRUO))

    if verbose:
        print("=== Estado inicial ===")
        imprimir_capas(cubo)
        print("Robots iniciales:", [(r.x, r.y, r.z, r.orientacion) for r in robots])
        print("Monstruos iniciales:", contar_monstruos())

    # 3) Bucle principal
    estasis_contador = 0
    prev_snap = snapshot_estado(cubo)

    for t in range(1, T_MAX + 1):
        # 3.1) Dinámica del mundo (monstruos)
        step_entorno(cubo, params, iteracion=t)

        # 3.2) Ticks de robots (reglas R1..R8 con logging)
        robots = [r for r in robots if r.tick(cubo, t)]

        # 3.3) Salida por iteración
        if verbose:
            print(f"\n--- Iteración {t} ---")
            imprimir_capas(cubo)
            print("Robots vivos:", [(r.x, r.y, r.z, r.orientacion) for r in robots])
            print("Monstruos:", contar_monstruos())

        # 3.4) Paradas globales
        if not robots:
            if verbose:
                print("\n⛔ No quedan robots.")
            break

        if contar_monstruos() == 0:
            if verbose:
                print("\n✅ No quedan monstruos.")
            break

        # Estasis: comparar snapshot del estado
        snap = snapshot_estado(cubo)
        if snap == prev_snap:
            estasis_contador += 1
        else:
            estasis_contador = 0
            prev_snap = snap

        if estasis_contador >= S_ESTASIS:
            if verbose:
                print(f"\n⚠️ Estasis detectada por {S_ESTASIS} ticks. Deteniendo simulación.")
            break

    # 4) Exportar memorias y calcular métricas
    rutas = [exportar_memoria_robot(r) for r in robots]
    total_kills = sum(r.kills for r in robots)
    n_monstruos_ini = params.Nmonstruos
    n_robots_ini = params.Nrobot if params.Nrobot > 0 else 1

    eficiencia_pct = (100.0 * total_kills / n_monstruos_ini) if n_monstruos_ini > 0 else 0.0
    eficiencia_media_por_robot = total_kills / n_robots_ini

    if verbose:
        for pth in rutas:
            print("Memoria guardada en:", pth)
        print("\n=== MÉTRICAS DE EFICIENCIA ===")
        print(f"Monstruos eliminados (total): {total_kills} / {n_monstruos_ini}  ({eficiencia_pct:.1f}%)")
        print(f"Eficiencia media por robot:   {eficiencia_media_por_robot:.3f}")
        print("\n=== Fin de la simulación ===")

    return cubo, robots
