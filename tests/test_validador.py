"""Suíte unittest:  py -m unittest discover -s tests -v"""

from __future__ import annotations

import itertools
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validador import gramatica  # noqa: E402
from validador.ap import AP_MISSAO, INVERSO, SIGMA_AP  # noqa: E402
from validador.lba import ALL_COMPROVANTES, LimiteFitaError, TransicaoALL  # noqa: E402
from validador.pipeline import SimboloInvalido, executar_all, executar_ap, executar_fluxo  # noqa: E402

PASTA = Path(__file__).resolve().parent


def casos(nome):
    return json.loads((PASTA / nome).read_text(encoding="utf-8"))


def referencia_ap(s: str) -> bool:
    """Definição direta de L_AP, independente do autômato e da gramática."""
    if s.count("#") != 1:
        return False
    rota, carga = s.split("#")
    if rota.count("*") != 1 or carga.count("=") != 1:
        return False
    ida, volta = rota.split("*")
    u, v = carga.split("=")
    return (len(ida) > 0 and all(c in "NSLO" for c in ida)
            and volta == "".join(INVERSO[c] for c in reversed(ida))
            and len(u) > 0 and len(u) == len(v) and all(c in "pg" for c in u + v))


def referencia_all(s: str) -> bool:
    if s.count("=") != 1:
        return False
    u, v = s.split("=")
    return len(u) > 0 and u == v and all(c in "pg" for c in u)


class TestModuloAP(unittest.TestCase):
    def test_casos_obrigatorios(self):
        for c in casos("casos_ap.json")["casos"]:
            with self.subTest(entrada=c["entrada"]):
                self.assertEqual(executar_ap(c["entrada"]).aceita, c["esperado"] == "aceita")

    def test_minimo_8_estados(self):
        self.assertGreaterEqual(len(AP_MISSAO.estados), 8)

    def test_rastro_mostra_estado_posicao_pilha(self):
        r = executar_ap("N*S#p=p")
        self.assertEqual(r.rastro[0].pilha, "$")
        self.assertEqual(r.rastro[2].pilha, "N$")
        self.assertEqual(r.rastro[-1].estado, "q7")
        self.assertEqual(r.rastro[-1].posicao, 7)

    def test_ap_igual_gramatica_e_referencia_exaustivo(self):
        """AP ≡ GLC ≡ definição, para TODAS as cadeias de comprimento ≤ 7 sobre um
        sub-alfabeto representativo, e para cadeias aleatórias estruturadas."""
        alfabeto = "NSL*#p=g"
        for n in range(0, 8):
            for t in itertools.product(alfabeto, repeat=n):
                s = "".join(t)
                ref = referencia_ap(s)
                self.assertEqual(AP_MISSAO.executar(s).aceita, ref, s)
                self.assertEqual(gramatica.pertence(s), ref, s)

    def test_aleatorio_estruturado(self):
        rnd = random.Random(42)
        for _ in range(3000):
            ida = "".join(rnd.choice("NSLO") for _ in range(rnd.randint(1, 8)))
            volta = "".join(INVERSO[c] for c in reversed(ida))
            if rnd.random() < 0.3:  # perturbação
                volta = volta[:-1] + rnd.choice("NSLO") if volta else volta
            u = "".join(rnd.choice("pg") for _ in range(rnd.randint(1, 8)))
            v = "".join(rnd.choice("pg") for _ in range(len(u) + rnd.choice([0, 0, 0, 1, -1])))
            s = f"{ida}*{volta}#{u}={v}"
            self.assertEqual(AP_MISSAO.executar(s).aceita, referencia_ap(s), s)
            self.assertEqual(gramatica.pertence(s), referencia_ap(s), s)

    def test_derivacao_termina_na_cadeia(self):
        passos = gramatica.derivacao_mais_a_esquerda("NNLLN*SOOSS#ppgp=ppgp")
        self.assertEqual(passos[0][0], "M")
        self.assertEqual(passos[-1][0], "NNLLN*SOOSS#ppgp=ppgp")


class TestModuloALL(unittest.TestCase):
    def test_casos_obrigatorios(self):
        for c in casos("casos_all.json")["casos"]:
            with self.subTest(entrada=c["entrada"]):
                self.assertEqual(executar_all(c["entrada"]).aceita, c["esperado"] == "aceita")

    def test_minimo_8_estados(self):
        self.assertGreaterEqual(len(ALL_COMPROVANTES.estados), 8)

    def test_exaustivo_ate_10(self):
        for n in range(0, 11):
            for t in itertools.product("pg=", repeat=n):
                s = "".join(t)
                self.assertEqual(ALL_COMPROVANTES.executar(s).aceita, referencia_all(s), s)

    def test_fita_limitada(self):
        """A fita tem sempre n + 2 células, marcadores intactos e cabeçote dentro dos limites."""
        for s in ["ppgpgggpp=ppgpgggpp", "ppgpgggpp=ppgpgggppg", "p=p", "", "=", "pgpg"]:
            r = ALL_COMPROVANTES.executar(s)
            for p in r.rastro:
                self.assertEqual(len(p.fita), len(s) + 2)
                self.assertEqual(p.fita[0], "<")
                self.assertEqual(p.fita[-1], ">")
                self.assertTrue(0 <= p.cabecote <= len(s) + 1)

    def test_transicao_que_viola_borda_e_recusada(self):
        with self.assertRaises(LimiteFitaError):
            ALL_COMPROVANTES._validar(TransicaoALL("q8", ">", "q8", ">", "D"))
        with self.assertRaises(LimiteFitaError):
            ALL_COMPROVANTES._validar(TransicaoALL("q6", "<", "q6", "X", "D"))

    def test_passos_quadraticos(self):
        """Termina em O(n²) passos: cota (n+2)² + n + 2."""
        for m in range(1, 15):
            s = "pg" * m
            s = s + "=" + s
            r = ALL_COMPROVANTES.executar(s)
            self.assertTrue(r.aceita)
            self.assertLessEqual(len(r.rastro), (len(s) + 2) ** 2 + len(s) + 2)


class TestIntegracao(unittest.TestCase):
    def test_tres_cenarios(self):
        for c in casos("casos_integracao.json")["casos"]:
            with self.subTest(entrada=c["entrada"]):
                f = executar_fluxo(c["entrada"])
                self.assertEqual("aceita" if f.ap.aceita else "rejeita", c["esperado_ap"])
                obtido = "nao_executado" if f.all is None else ("aceita" if f.all.aceita else "rejeita")
                self.assertEqual(obtido, c["esperado_all"])

    def test_simbolo_fora_do_alfabeto(self):
        with self.assertRaises(SimboloInvalido) as ctx:
            executar_fluxo("NNLLX*SOOSS#ppgp=ppgp")
        self.assertIn("'X' na posição 4", str(ctx.exception))
        with self.assertRaises(SimboloInvalido):
            executar_all("ppgpgggpp=ppgpgggpx")
        self.assertNotIn("X", SIGMA_AP)


if __name__ == "__main__":
    unittest.main()
