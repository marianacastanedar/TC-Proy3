"""Cinta de la máquina de Turing."""


class Cinta:
    """Cinta infinita hacia ambos lados. Lo que no está guardado es blank."""

    def __init__(self, cadena_inicial=""):
        # Guardamos solo las celdas con símbolo; así no hay que mover listas
        # para simular una cinta infinita.
        self.celdas = {}
        for posicion, simbolo in enumerate(cadena_inicial):
            self.celdas[posicion] = simbolo

    def leer(self, pos):
        """Devuelve el símbolo en `pos`, o None si es blank."""
        return self.celdas.get(pos)

    def escribir(self, pos, simbolo):
        """Escribe un símbolo en `pos`. Escribir None borra la celda (blank)."""
        if simbolo is None:
            self.celdas.pop(pos, None)
        else:
            self.celdas[pos] = simbolo

    def contenido(self):
        """Texto de la cinta de extremo a extremo, sin blanks sobrantes."""
        if not self.celdas:
            return ""
        inicio = min(self.celdas)
        fin = max(self.celdas)
        return "".join(self.celdas.get(p, "") for p in range(inicio, fin + 1))

    def rango_usado(self, cabezal):
        """Qué parte de la cinta hay que mostrar en una ID: lo escrito más el cabezal."""
        if not self.celdas:
            return cabezal, cabezal
        inicio = min(min(self.celdas), cabezal)
        fin = max(max(self.celdas), cabezal)
        return inicio, fin
