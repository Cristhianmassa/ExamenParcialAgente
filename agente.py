# =====================================================
# agente.py — Agente Robot (reglas R1..R8 + logging)
# =====================================================
from dataclasses import dataclass
from typing import Literal, Dict, Any, List, Tuple

# --- Debe concordar con entorno.py ---
ZV = 0
ZL = 1
ROBOT = 3
MONSTRUO = 4

# --- Orientaciones (±X, ±Y, ±Z) ---
Orient = Literal["X+", "X-", "Y+", "Y-", "Z+", "Z-"]

def celda_frontal(x: int, y: int, z: int, orient: Orient) -> Tuple[int, int, int]:
    if orient == "X+": return (x + 1, y, z)
    if orient == "X-": return (x - 1, y, z)
    if orient == "Y+": return (x, y + 1, z)
    if orient == "Y-": return (x, y - 1, z)
    if orient == "Z+": return (x, y, z + 1)
    if orient == "Z-": return (x, y, z - 1)
    raise ValueError("Orientación inválida")

OPUESTA: Dict[Orient, Orient] = {
    "X+": "X-", "X-": "X+",
    "Y+": "Y-", "Y-": "Y+",
    "Z+": "Z-", "Z-": "Z+",
}

# Ciclos de 90° (4 ortogonales) por orientación — orden fijo (cíclico)
CICLOS_ORTO: Dict[Orient, List[Orient]] = {
    "X+": ["Y+", "Z+", "Y-", "Z-"],
    "X-": ["Y+", "Z-", "Y-", "Z+"],
    "Y+": ["Z+", "X-", "Z-", "X+"],
    "Y-": ["Z+", "X+", "Z-", "X-"],
    "Z+": ["X+", "Y-", "X-", "Y+"],
    "Z-": ["X+", "Y+", "X-", "Y-"],
}

def rotar_90(orient: Orient, lado_idx: int) -> Tuple[Orient, int]:
    opciones = CICLOS_ORTO[orient]
    nueva = opciones[lado_idx % 4]
    return nueva, (lado_idx + 1) % 4

def vecinos_locales(x: int, y: int, z: int, orient: Orient) -> Dict[str, Any]:
    frente = celda_frontal(x, y, z, orient)
    atras  = celda_frontal(x, y, z, OPUESTA[orient])
    costados = [celda_frontal(x, y, z, o) for o in CICLOS_ORTO[orient]]
    return {"frente": frente, "atras": atras, "costados": costados}

# --- Sensores de apoyo ---
def detectar_monstruo_cinco_lados(cubo, x: int, y: int, z: int, orient: Orient) -> bool:
    v = vecinos_locales(x, y, z, orient)
    chequear = [v["frente"], *v["costados"]]  # 5 caras (excluye atrás)
    N = len(cubo)
    for (nx, ny, nz) in chequear:
        if 0 <= nx < N and 0 <= ny < N and 0 <= nz < N:
            if cubo[nx][ny][nz] == MONSTRUO:
                return True
    return False

def frontal_estado(cubo, x: int, y: int, z: int, orient: Orient) -> str:
    nx, ny, nz = celda_frontal(x, y, z, orient)
    N = len(cubo)
    if not (0 <= nx < N and 0 <= ny < N and 0 <= nz < N):
        return "BORDE"
    valor = cubo[nx][ny][nz]
    return "ZL" if valor == ZL else ("ZV" if valor == ZV else ("ROBOT" if valor == ROBOT else ("MONSTRUO" if valor == MONSTRUO else "DESCONOCIDO")))

# =======================
#        ROBOT
# =======================
@dataclass
class Robot:
    x: int
    y: int
    z: int
    orientacion: Orient = "X+"
    lado_idx: int = 0                      # índice para el ciclo de 90°
    kills: int = 0                         # monstruos eliminados por este robot
    memoria: List[Dict[str, Any]] = None   # tabla de logs por tick

    def __post_init__(self):
        if self.memoria is None:
            self.memoria = []

    def _log_tick(self, t: int, regla: str, accion: str, percep: Dict[str, Any],
                  frontal: str, pre: Tuple[int,int,int,Orient], post: Tuple[int,int,int,Orient]):
        self.memoria.append({
            "t": t,
            "regla": regla,
            "accion": accion,
            "percepcion": percep,
            "frontal_estado": frontal,
            "pos_pre": (pre[0], pre[1], pre[2]),
            "ori_pre": pre[3],
            "pos_post": (post[0], post[1], post[2]),
            "ori_post": post[3],
            "kills": self.kills
        })

    def tick(self, cubo, t: int) -> bool:
        """
        Reglas con prioridad:
        R1 (energómetro) → R2 (borde/ZV) → R3 (robot al frente) → R4 (monstruo al frente)
        → R5 (M=TRUE & frontal ZL) → R6 (M=TRUE & frontal bloqueado) → R7 (neutro ZL) → R8 (neutro bloqueado).
        Devuelve False si el robot fue destruido; True si sigue activo.
        """
        pre = (self.x, self.y, self.z, self.orientacion)
        percep = {
            "energometro": False,
            "robot_frente": False,
            "monstroscopio": False,
            "vacuscopio": False
        }

        # R1. Monstruo en mi celda (aniquilación mutua)
        if cubo[self.x][self.y][self.z] == MONSTRUO:
            cubo[self.x][self.y][self.z] = ZV
            self.kills += 1
            self._log_tick(t, "R1_MONSTRUO_EN_MI_CELDA", "vacuumator", {**percep, "energometro": True}, "AQUI", pre, (self.x, self.y, self.z, self.orientacion))
            return False

        # Sensado frontal (una vez)
        f_estado = frontal_estado(cubo, self.x, self.y, self.z, self.orientacion)

        # R2. Pared/ZV al frente
        if f_estado in ("BORDE", "ZV"):
            percep["vacuscopio"] = "borde" if f_estado == "BORDE" else True
            self.orientacion, self.lado_idx = rotar_90(self.orientacion, self.lado_idx)
            post = (self.x, self.y, self.z, self.orientacion)
            self._log_tick(t, "R2_BLOQUEO_FRENTE", "rotar_90", percep, f_estado, pre, post)
            return True

        # R3. Robot al frente (protocolo determinista — TODO: coordinación global)
        if f_estado == "ROBOT":
            percep["robot_frente"] = True
            # Versión local (provisional): rota para evitar choque y registra R3
            self.orientacion, self.lado_idx = rotar_90(self.orientacion, self.lado_idx)
            post = (self.x, self.y, self.z, self.orientacion)
            self._log_tick(t, "R3_ROBOT_AL_FRENTE", "rotar_90_por_robot", percep, f_estado, pre, post)
            return True

        # R4. Monstruo al frente
        if f_estado == "MONSTRUO":
            # avanzar a la celda con monstruo; aniquilación se resuelve al inicio del próximo tick (R1)
            nx, ny, nz = celda_frontal(self.x, self.y, self.z, self.orientacion)
            cubo[self.x][self.y][self.z] = ZL
            cubo[nx][ny][nz] = ROBOT
            self.x, self.y, self.z = nx, ny, nz
            post = (self.x, self.y, self.z, self.orientacion)
            self._log_tick(t, "R4_MONSTRUO_FRENTE", "avanzar_a_monstruo", percep, f_estado, pre, post)
            return True

        # Monstroscopio (5 caras)
        percep["monstroscopio"] = detectar_monstruo_cinco_lados(cubo, self.x, self.y, self.z, self.orientacion)

        # R5. M=TRUE y frontal ZL → avanzar
        if percep["monstroscopio"] and f_estado == "ZL":
            nx, ny, nz = celda_frontal(self.x, self.y, self.z, self.orientacion)
            cubo[self.x][self.y][self.z] = ZL
            cubo[nx][ny][nz] = ROBOT
            self.x, self.y, self.z = nx, ny, nz
            post = (self.x, self.y, self.z, self.orientacion)
            self._log_tick(t, "R5_MONSTROSCOPIO_AVANZAR", "avanzar", percep, f_estado, pre, post)
            return True

        # R6. M=TRUE y frontal bloqueado (ZV/BORDE/ROBOT) → rotar
        if percep["monstroscopio"] and f_estado in ("ZV", "BORDE", "ROBOT"):
            self.orientacion, self.lado_idx = rotar_90(self.orientacion, self.lado_idx)
            post = (self.x, self.y, self.z, self.orientacion)
            self._log_tick(t, "R6_MONSTROSCOPIO_BLOQUEO", "rotar_90", percep, f_estado, pre, post)
            return True

        # R7. Neutro (M=FALSE) con frontal ZL → avanzar
        if (not percep["monstroscopio"]) and f_estado == "ZL":
            nx, ny, nz = celda_frontal(self.x, self.y, self.z, self.orientacion)
            cubo[self.x][self.y][self.z] = ZL
            cubo[nx][ny][nz] = ROBOT
            self.x, self.y, self.z = nx, ny, nz
            post = (self.x, self.y, self.z, self.orientacion)
            self._log_tick(t, "R7_NEUTRO_AVANZAR", "avanzar", percep, f_estado, pre, post)
            return True

        # R8. Neutro bloqueado → rotar
        self.orientacion, self.lado_idx = rotar_90(self.orientacion, self.lado_idx)
        post = (self.x, self.y, self.z, self.orientacion)
        self._log_tick(t, "R8_NEUTRO_BLOQUEO", "rotar_90", percep, f_estado, pre, post)
        return True
