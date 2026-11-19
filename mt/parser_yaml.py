"""Lee el archivo YAML de una máquina de Turing y lo valida."""

import yaml

CLAVES_OBLIGATORIAS = ["q_states", "alphabet", "tape_alphabet", "delta", "simulation_strings"]
MOVIMIENTOS_VALIDOS = {"L", "R", "S"}


class MaquinaDatos:
    """Guarda los datos ya validados y normalizados de una máquina de Turing."""

    def __init__(self, estados, inicial, finales, alfabeto, alfabeto_cinta, transiciones, cadenas):
        self.estados = estados
        self.inicial = inicial
        self.finales = finales
        self.alfabeto = alfabeto
        self.alfabeto_cinta = alfabeto_cinta
        self.transiciones = transiciones
        self.cadenas = cadenas


def _a_str(valor):
    """Convierte estados y símbolos a str, dejando el blank (None) tal cual."""
    if valor is None:
        return None
    return str(valor)


def cargar_maquina(ruta):
    """Lee el YAML en `ruta`, lo valida y devuelve un MaquinaDatos."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = yaml.safe_load(archivo)

    for clave in CLAVES_OBLIGATORIAS:
        if clave not in datos:
            raise ValueError(f"Falta la clave '{clave}' en el archivo")

    q_states = datos["q_states"]
    estados = {_a_str(e) for e in q_states["q_list"]}
    inicial = _a_str(q_states["initial"])

    final_crudo = q_states["final"]
    if isinstance(final_crudo, list):
        finales = {_a_str(e) for e in final_crudo}
    else:
        finales = {_a_str(final_crudo)}

    alfabeto = {_a_str(s) for s in datos["alphabet"]}
    # el alfabeto de cinta real incluye también el de entrada y el blank
    alfabeto_cinta = {_a_str(s) for s in datos["tape_alphabet"]} | alfabeto | {None}

    if inicial not in estados:
        raise ValueError(f"El estado inicial '{inicial}' no está en q_list")
    for estado_final in finales:
        if estado_final not in estados:
            raise ValueError(f"El estado final '{estado_final}' no está en q_list")

    transiciones = _leer_transiciones(datos["delta"], estados, alfabeto_cinta)
    cadenas = _leer_cadenas(datos["simulation_strings"], alfabeto)

    return MaquinaDatos(estados, inicial, finales, alfabeto, alfabeto_cinta, transiciones, cadenas)


def _leer_transiciones(delta_crudo, estados, alfabeto_cinta):
    """Normaliza la lista `delta` del YAML y valida cada transición."""
    transiciones = []
    llaves_usadas = set()

    for fila in delta_crudo:
        params = fila["params"]
        output = fila["output"]

        estado_origen = _a_str(params["initial_state"])
        cache_entrada = _a_str(params["mem_cache_value"])
        simbolo_leido = _a_str(params["tape_input"])

        estado_destino = _a_str(output["final_state"])
        cache_salida = _a_str(output["mem_cache_value"])
        simbolo_escrito = _a_str(output["tape_output"])
        movimiento = output["tape_displacement"]

        if estado_origen not in estados:
            raise ValueError(f"La transición usa un estado inexistente: '{estado_origen}'")
        if estado_destino not in estados:
            raise ValueError(f"La transición usa un estado inexistente: '{estado_destino}'")
        if simbolo_leido not in alfabeto_cinta:
            raise ValueError(f"El símbolo leído '{simbolo_leido}' no está en el alfabeto de cinta")
        if simbolo_escrito not in alfabeto_cinta:
            raise ValueError(f"El símbolo escrito '{simbolo_escrito}' no está en el alfabeto de cinta")
        if movimiento not in MOVIMIENTOS_VALIDOS:
            raise ValueError(f"Movimiento inválido '{movimiento}' (debe ser L, R o S)")

        llave = (estado_origen, cache_entrada, simbolo_leido)
        if llave in llaves_usadas:
            raise ValueError(f"Hay dos transiciones para (estado, cache, símbolo) = {llave}")
        llaves_usadas.add(llave)

        transiciones.append({
            "estado_origen": estado_origen,
            "cache_entrada": cache_entrada,
            "simbolo_leido": simbolo_leido,
            "estado_destino": estado_destino,
            "cache_salida": cache_salida,
            "simbolo_escrito": simbolo_escrito,
            "movimiento": movimiento,
        })

    return transiciones


def _leer_cadenas(cadenas_crudas, alfabeto):
    """Avisa si una cadena usa símbolos fuera del alfabeto, pero no detiene el programa."""
    cadenas = []
    for cadena in cadenas_crudas:
        cadena = str(cadena)
        simbolos_invalidos = [s for s in cadena if s not in alfabeto]
        if simbolos_invalidos:
            print(f"Aviso: la cadena '{cadena}' usa símbolos fuera del alfabeto {simbolos_invalidos}, se rechazará")
        cadenas.append(cadena)
    return cadenas
