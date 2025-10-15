# =====================================================
# main.py - Pruebas
# =====================================================
#cubo[0][0][0] = 0 (esquina izquierda, arriba) x,y,z
#cubo[4][0][0] = 0 (esquina derecha, arriba)

#from entorno import ParamEntorno, imprimir_capas, MONSTRUO, obtener_posiciones, construir_entorno, colocar_agentes, \
#    obtener_posiciones_agentes
from simulacion import simular

# Crear entorno
#params = ParamEntorno(N=5, Pfree=0.5, Psoft=0.5, Nrobot=2, Nmonstruos=2 , p_monstruo=0.8, K_monstruo=10)
#cubo  = construir_entorno(params)

# Colocar agentes en el entorno
#colocar_agentes(cubo, params)

# Verificaciones
# print(f"\nCubo creado con dimensiones: {params.N}x{params.N}x{params.N}")
# print(f"Tipo de dato: {type(entorno)}")
# print(f"Número total de celdas: {params.N ** 3}")
# print(f"Valor inicial de la primera celda [0][0][0]: {entorno[0][0][0]}")



# Mostrar posiciones
#posiciones = obtener_posiciones_agentes(cubo)

#print("\n📍 Posiciones de los agentes:")
#print("Robots:", posiciones["robots"])
#print("Monstruos:", posiciones["monstruos"])


#params = ParamEntorno(N=5, Pfree=0.7, Psoft=0.3, Nrobot=2, Nmonstruos=3, seed=42, K_monstruo=2, p_monstruo=0.7)
#cubo, robots = simular(params, T_MAX=10)

#print("Estado inicial:")
#imprimir_capas(cubo)

#print("Robots vivos:", [(r.x, r.y, r.z, r.orientacion) for r in robots])
#print("Monstruos restantes:", len(obtener_posiciones(cubo, MONSTRUO)))
#imprimir_capas(cubo)

from entorno import ParamEntorno, obtener_posiciones, MONSTRUO
from simulacion import simular

params = ParamEntorno(
    N=5, Pfree=0.70, Psoft=0.30,
    Nrobot=2, Nmonstruos=3,
    seed=42,
    K_monstruo=2, p_monstruo=0.7
)

cubo, robots = simular(params, T_MAX=200, verbose=True, S_ESTASIS=20)
print("Resumen final → Robots vivos:", [(r.x, r.y, r.z, r.orientacion) for r in robots])
print("Monstruos restantes:", len(obtener_posiciones(cubo, MONSTRUO)))
