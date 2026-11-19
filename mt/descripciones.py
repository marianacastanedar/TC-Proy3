"""Formato de las descripciones instantáneas (IDs) de la máquina."""

SIMBOLO_BLANK = "B"


def _texto(simbolo):
    return SIMBOLO_BLANK if simbolo is None else simbolo


def formatear_id(cinta, cabezal, estado, cache):
    """Arma una ID: lo que hay a la izquierda del cabezal, [estado, cache] y el resto."""
    inicio, fin = cinta.rango_usado(cabezal)
    izquierda = "".join(_texto(cinta.leer(p)) for p in range(inicio, cabezal))
    derecha = "".join(_texto(cinta.leer(p)) for p in range(cabezal, fin + 1))
    return f"{izquierda}[{estado}, {_texto(cache)}]{derecha}"


def imprimir_ids(ids):
    """Imprime la lista de IDs, una por línea, con el ⊢ que pide el formato."""
    for paso, id_texto in enumerate(ids):
        prefijo = "    " if paso == 0 else " ⊢ "
        print(f"Paso {paso}:{prefijo}{id_texto}")
