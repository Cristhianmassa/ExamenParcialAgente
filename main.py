# =====================================================
# main.py - Pruebas
# =====================================================

from entorno import ParamEntorno, _validar_parametros, crear_cubo_vacio

# 1. Crear parámetros y validar
params = ParamEntorno(N=3, Pfree=0.6, Psoft=0.4)
_validar_parametros(params)

# 2. Crear cubo vacío
cubo = crear_cubo_vacio(params.N)

# 3. Verificaciones
print(f"\nCubo creado con dimensiones: {params.N}x{params.N}x{params.N}")
print(f"Tipo de dato: {type(cubo)}")
print(f"Número total de celdas: {params.N ** 3}")
print(f"Valor inicial de la primera celda [0][0][0]: {cubo[0][0][0]}")

