# =====================================================
# main.py - Pruebas
# =====================================================
#cubo[0][0][0] = 0 (esquina izquierda, arriba) x,y,z
#cubo[4][0][0] = 0 (esquina derecha, arriba)

from entorno import ParamEntorno, _validar_parametros, imprimir_capas, construir_entorno, colocar_agentes, \
    obtener_posiciones_agentes

from agente import Agente

# 2. Crear entorno
params = ParamEntorno(N=5, Pfree=0.5, Psoft=0.5, Nrobot=2, Nmonstruos=2)
entorno = construir_entorno(params)

# 2. Crear agentes
robot = Agente(tipo="robot", codigo=3)
monstruo = Agente(tipo="monstruo", codigo=4)

# 3. Colocar agentes en el entorno
colocar_agentes(entorno, params)

# Verificaciones
print(f"\nCubo creado con dimensiones: {params.N}x{params.N}x{params.N}")
print(f"Tipo de dato: {type(entorno)}")
print(f"Número total de celdas: {params.N ** 3}")
print(f"Valor inicial de la primera celda [0][0][0]: {entorno[0][0][0]}")

print(f"\n🌌 Entorno generado aleatoriamente (N={params.N})")
imprimir_capas(entorno)

# Mostrar posiciones
posiciones = obtener_posiciones_agentes(entorno)

print("\n📍 Posiciones de los agentes:")
print("Robots:", posiciones["robots"])
print("Monstruos:", posiciones["monstruos"])

