# =====================================================
# AGENTES - Estructura basica
# =====================================================

from dataclasses import dataclass
import random
from entorno import ZL

@dataclass
class Agente:
    """
    Representa un agente dentro del entorno.
    """
    tipo: str        # "robot" o "monstruo"
    codigo: int      # 3 para robot, 4 para monstruo
    x: int = 0
    y: int = 0
    z: int = 0

