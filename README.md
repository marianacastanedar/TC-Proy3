# Simulador de Máquinas de Turing

Simulador en Python de una máquina de Turing de una sola cinta, donde el estado
de la máquina es un par **[estado, valor de caché]**. Las transiciones, los
alfabetos y las cadenas a simular se definen en un archivo YAML; el programa
imprime todas las descripciones instantáneas (IDs) de la simulación y dice si
cada cadena fue aceptada o rechazada.

## Requisitos e instalación

```bash
python -m venv .venv
.venv\Scripts\activate      # en Windows
pip install -r requirements.txt
```

La única dependencia externa es `pyyaml`.

## Cómo ejecutar

```bash
python main.py maquinas/reconocedora.yaml
python main.py maquinas/alteradora.yaml
```

Con `--solo-resumen` se omiten las IDs y solo se muestra el resultado de cada
cadena:

```bash
python main.py maquinas/reconocedora.yaml --solo-resumen
```

## Cómo correr las pruebas

```bash
python -m unittest discover pruebas
```

## Formato del YAML

```yaml
q_states:
  q_list: ['0', '1', '2']
  initial: '0'
  final: '2'            # puede ser un solo valor o una lista
alphabet:
  - a
  - b
tape_alphabet:
  - X
  -                      # entrada vacía = null = blank
delta:
  - params:
      initial_state: '0'
      mem_cache_value:   # vacío = blank
      tape_input: a
    output:
      final_state: '1'
      mem_cache_value: a
      tape_output:       # vacío = blank
      tape_displacement: R   # L, R o S
simulation_strings:
  - aab
  - ab
```

El alfabeto de cinta real que usa el programa es la unión de `tape_alphabet`,
`alphabet` y el blank.

## Arquitectura

```
YAML → parser_yaml → MaquinaTuring (transiciones en dict) → simular() → Cinta + IDs → main imprime
```

- `main.py`: punto de entrada por línea de comandos; imprime el resumen de la
  máquina, las IDs de cada cadena y la tabla de resultados.
- `mt/parser_yaml.py`: lee el YAML, valida las claves y los datos, y normaliza
  estados y símbolos a `str`.
- `mt/cinta.py`: clase `Cinta`, la cinta de la máquina como diccionario
  `{posición: símbolo}`.
- `mt/maquina.py`: clase `MaquinaTuring`, guarda las transiciones en un
  diccionario con llave `(estado, cache, símbolo)` y simula paso a paso.
- `mt/descripciones.py`: da formato a las descripciones instantáneas (IDs).

## Las dos máquinas

### Reconocedora: L = { aⁿbⁿcⁿ | n ≥ 1 }

En cada vuelta marca una `a` con `X`, una `b` con `Y` y una `c` con `Z`, y
regresa para la siguiente vuelta. Cuando ya no quedan `a` sin marcar, revisa
que lo que sigue sean solo `Y` y `Z`. No usa la caché (siempre queda en
blank). Es un lenguaje que no es libre de contexto.

| Estado | Lee   | Nuevo estado | Escribe | Mov | Idea |
|--------|-------|--------------|---------|-----|------|
| q0 | a     | q1 | X     | R | marca una a |
| q0 | Y     | q4 | Y     | R | ya no hay a: verificar el resto |
| q1 | a     | q1 | a     | R | busca una b |
| q1 | Y     | q1 | Y     | R | |
| q1 | b     | q2 | Y     | R | marca una b |
| q2 | b     | q2 | b     | R | busca una c |
| q2 | Z     | q2 | Z     | R | |
| q2 | c     | q3 | Z     | L | marca una c y regresa |
| q3 | a     | q3 | a     | L | regresa hasta la última X |
| q3 | b     | q3 | b     | L | |
| q3 | Y     | q3 | Y     | L | |
| q3 | Z     | q3 | Z     | L | |
| q3 | X     | q0 | X     | R | siguiente vuelta |
| q4 | Y     | q4 | Y     | R | solo deben quedar Y... |
| q4 | Z     | q4 | Z     | R | ...y Z |
| q4 | blank | q5 | blank | S | fin: acepta |

| Cadena | Resultado | Pasos | Cinta final |
|--------|-----------|-------|-------------|
| `aabbcc`    | ACEPTADA  | 23 | `XXYYZZ` |
| `aaabbbccc` | ACEPTADA  | 46 | `XXXYYYZZZ` |
| `aabbbcc`   | RECHAZADA | 24 | `XXYYbZZ` |
| `abcabc`    | RECHAZADA | 7  | `XYZabc` |

### Alteradora: invertir una cadena w ∈ {a, b}*

Pone un `#` al final de la entrada. Luego, una y otra vez, toma el último
símbolo no copiado de `w`, lo marca con `X`, lo guarda en la caché, viaja a la
derecha y lo escribe al final de la copia. Al terminar borra las `X` y el `#`,
y en la cinta queda `wᴿ`. Esta máquina sí usa la caché del estado.

| Estado | Caché | Lee   | Nuevo estado | Nueva caché | Escribe | Mov | Idea |
|--------|-------|-------|--------------|-------------|---------|-----|------|
| q0 | B | a     | q0 | B | a     | R | ir al final de w |
| q0 | B | b     | q0 | B | b     | R | |
| q0 | B | blank | q1 | B | #     | L | pone el separador |
| q1 | B | X     | q1 | B | X     | L | busca el último símbolo sin copiar |
| q1 | B | a     | q2 | a | X     | R | guarda `a` en caché |
| q1 | B | b     | q2 | b | X     | R | guarda `b` en caché |
| q1 | B | blank | q4 | B | blank | R | ya copió todo: limpiar |
| q2 | a | X / # / a / b | q2 | a | (igual) | R | viaja a la derecha cargando `a` |
| q2 | a | blank | q3 | B | a     | L | escribe la `a` al final |
| q2 | b | X / # / a / b | q2 | b | (igual) | R | viaja cargando `b` |
| q2 | b | blank | q3 | B | b     | L | escribe la `b` al final |
| q3 | B | a     | q3 | B | a     | L | regresa hasta el # |
| q3 | B | b     | q3 | B | b     | L | |
| q3 | B | #     | q1 | B | #     | L | pasa al lado de w |
| q4 | B | X     | q4 | B | blank | R | borra las marcas |
| q4 | B | #     | q5 | B | blank | R | borra el # y acepta |

| Cadena | Resultado | Pasos | Cinta final |
|--------|-----------|-------|-------------|
| `aabbb`  | ACEPTADA | 78  | `bbbaa` |
| `abbab`  | ACEPTADA | 78  | `babba` |
| `baaabb` | ACEPTADA | 105 | `bbaaab` |
| `aaaaab` | ACEPTADA | 105 | `baaaaa` |

## Video

Video: [(Video en youtube)](https://youtu.be/f2RxisPB31c)

## Integrantes

- Mariana Castañeda
