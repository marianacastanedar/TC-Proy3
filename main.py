"""Punto de entrada: simula una máquina de Turing a partir de un YAML.

Uso: python main.py maquinas/reconocedora.yaml [--solo-resumen]
"""

import sys

# La consola de Windows no siempre usa UTF-8, y el símbolo ⊢ de las IDs lo necesita.
sys.stdout.reconfigure(encoding="utf-8")

from mt.parser_yaml import cargar_maquina
from mt.maquina import MaquinaTuring
from mt.descripciones import imprimir_ids

ANCHO_SEPARADOR = 46


def imprimir_resumen_maquina(datos):
    print(f"Estados: {sorted(datos.estados)}")
    print(f"Estado inicial: {datos.inicial}")
    print(f"Estado(s) final(es): {sorted(datos.finales)}")
    print(f"Alfabeto: {sorted(datos.alfabeto)}")
    print(f"Alfabeto de cinta: {sorted(s for s in datos.alfabeto_cinta if s is not None)}")
    print(f"Número de transiciones: {len(datos.transiciones)}")


def imprimir_resultado(resultado, solo_resumen):
    print("=" * ANCHO_SEPARADOR)
    print(f"Cadena: {resultado.cadena}")
    print("-" * ANCHO_SEPARADOR)
    if not solo_resumen:
        imprimir_ids(resultado.ids)
        print("-" * ANCHO_SEPARADOR)
    texto = "ACEPTADA" if resultado.aceptada else "RECHAZADA"
    print(f"Resultado: {texto} en {resultado.pasos} pasos")
    print(f"Cinta final: {resultado.cinta_final}")


def imprimir_tabla_resumen(resultados):
    print("=" * ANCHO_SEPARADOR)
    print("Resumen:")
    for resultado in resultados:
        texto = "aceptada" if resultado.aceptada else "rechazada"
        print(f"  {resultado.cadena}: {texto}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo.yaml> [--solo-resumen]")
        sys.exit(1)

    ruta = sys.argv[1]
    solo_resumen = "--solo-resumen" in sys.argv[2:]

    try:
        datos = cargar_maquina(ruta)
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)

    maquina = MaquinaTuring(datos)
    imprimir_resumen_maquina(datos)

    resultados = [maquina.simular(cadena) for cadena in datos.cadenas]
    for resultado in resultados:
        imprimir_resultado(resultado, solo_resumen)

    imprimir_tabla_resumen(resultados)


if __name__ == "__main__":
    main()
