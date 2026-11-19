"""Pruebas del parser y de las dos máquinas, con unittest."""

import os
import tempfile
import unittest

import yaml

from mt.parser_yaml import cargar_maquina
from mt.maquina import MaquinaTuring

RUTA_RECONOCEDORA = os.path.join("maquinas", "reconocedora.yaml")
RUTA_ALTERADORA = os.path.join("maquinas", "alteradora.yaml")


def _guardar_yaml_temporal(datos):
    """Escribe `datos` en un YAML temporal y devuelve su ruta."""
    archivo = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.safe_dump(datos, archivo, allow_unicode=True)
    archivo.close()
    return archivo.name


class PruebasParser(unittest.TestCase):
    def test_falla_si_falta_una_clave(self):
        with open(RUTA_RECONOCEDORA, encoding="utf-8") as archivo:
            datos = yaml.safe_load(archivo)
        del datos["delta"]
        ruta = _guardar_yaml_temporal(datos)
        try:
            with self.assertRaises(ValueError):
                cargar_maquina(ruta)
        finally:
            os.remove(ruta)

    def test_falla_si_hay_transicion_repetida(self):
        with open(RUTA_RECONOCEDORA, encoding="utf-8") as archivo:
            datos = yaml.safe_load(archivo)
        datos["delta"].append(datos["delta"][0])
        ruta = _guardar_yaml_temporal(datos)
        try:
            with self.assertRaises(ValueError):
                cargar_maquina(ruta)
        finally:
            os.remove(ruta)


class PruebasReconocedora(unittest.TestCase):
    def setUp(self):
        self.maquina = MaquinaTuring(cargar_maquina(RUTA_RECONOCEDORA))

    def test_acepta_aabbcc(self):
        resultado = self.maquina.simular("aabbcc")
        self.assertTrue(resultado.aceptada)
        self.assertEqual(resultado.pasos, 23)
        self.assertEqual(resultado.cinta_final, "XXYYZZ")

    def test_acepta_aaabbbccc(self):
        resultado = self.maquina.simular("aaabbbccc")
        self.assertTrue(resultado.aceptada)
        self.assertEqual(resultado.pasos, 46)
        self.assertEqual(resultado.cinta_final, "XXXYYYZZZ")

    def test_rechaza_aabbbcc(self):
        resultado = self.maquina.simular("aabbbcc")
        self.assertFalse(resultado.aceptada)
        self.assertEqual(resultado.pasos, 24)

    def test_rechaza_abcabc(self):
        resultado = self.maquina.simular("abcabc")
        self.assertFalse(resultado.aceptada)
        self.assertEqual(resultado.pasos, 7)

    def test_rechaza_simbolo_fuera_del_alfabeto(self):
        # 'z' no está en el alfabeto de esta máquina; debe rechazarse sin romper nada.
        resultado = self.maquina.simular("aazbcc")
        self.assertFalse(resultado.aceptada)


class PruebasAlteradora(unittest.TestCase):
    def setUp(self):
        self.maquina = MaquinaTuring(cargar_maquina(RUTA_ALTERADORA))

    def _probar_inversion(self, cadena):
        resultado = self.maquina.simular(cadena)
        self.assertTrue(resultado.aceptada)
        self.assertEqual(resultado.cinta_final, cadena[::-1])

    def test_invierte_aabbb(self):
        self._probar_inversion("aabbb")

    def test_invierte_abbab(self):
        self._probar_inversion("abbab")

    def test_invierte_baaabb(self):
        self._probar_inversion("baaabb")

    def test_invierte_aaaaab(self):
        self._probar_inversion("aaaaab")


if __name__ == "__main__":
    unittest.main()
