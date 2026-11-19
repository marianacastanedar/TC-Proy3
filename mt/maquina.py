"""Máquina de Turing: transiciones y simulación."""

from mt.cinta import Cinta
from mt.descripciones import formatear_id


class ResultadoSimulacion:
    """Lo que devuelve una simulación: suficiente para imprimir el reporte."""

    def __init__(self, cadena, aceptada, ids, pasos, cinta_final, motivo):
        self.cadena = cadena
        self.aceptada = aceptada
        self.ids = ids
        self.pasos = pasos
        self.cinta_final = cinta_final
        self.motivo = motivo


class MaquinaTuring:
    """Máquina de Turing de una cinta, con memoria en el estado (estado, cache)."""

    def __init__(self, datos):
        self.estados = datos.estados
        self.inicial = datos.inicial
        self.finales = datos.finales
        self.alfabeto = datos.alfabeto
        self.alfabeto_cinta = datos.alfabeto_cinta
        self.transiciones = self._construir_transiciones(datos.transiciones)

    def _construir_transiciones(self, lista_transiciones):
        # Llave: (estado, cache, símbolo leído). Así buscar la transición es un solo acceso.
        transiciones = {}
        for t in lista_transiciones:
            llave = (t["estado_origen"], t["cache_entrada"], t["simbolo_leido"])
            valor = (t["estado_destino"], t["cache_salida"], t["simbolo_escrito"], t["movimiento"])
            transiciones[llave] = valor
        return transiciones

    def simular(self, cadena, max_pasos=10000):
        """Simula la máquina sobre `cadena` y devuelve un ResultadoSimulacion."""
        cinta = Cinta(cadena)
        cabezal = 0
        estado = self.inicial
        cache = None
        ids = [formatear_id(cinta, cabezal, estado, cache)]
        pasos = 0

        while True:
            if estado in self.finales:
                aceptada, motivo = True, "aceptada"
                break

            simbolo = cinta.leer(cabezal)
            llave = (estado, cache, simbolo)
            if llave not in self.transiciones:
                aceptada, motivo = False, "sin transición disponible"
                break

            if pasos >= max_pasos:
                aceptada, motivo = False, "no se detuvo (posible ciclo infinito)"
                break

            estado, cache, simbolo_escrito, movimiento = self.transiciones[llave]
            cinta.escribir(cabezal, simbolo_escrito)
            if movimiento == "R":
                cabezal += 1
            elif movimiento == "L":
                cabezal -= 1
            # movimiento "S" no mueve el cabezal

            pasos += 1
            ids.append(formatear_id(cinta, cabezal, estado, cache))

        return ResultadoSimulacion(cadena, aceptada, ids, pasos, cinta.contenido(), motivo)
