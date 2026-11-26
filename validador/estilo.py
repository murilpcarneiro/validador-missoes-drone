"""Formatação de terminal: cores ANSI e tabelas com bordas.

As cores só são usadas quando a saída é um terminal interativo; com a saída
redirecionada para arquivo, com NO_COLOR definida ou com --sem-cor, o texto sai limpo.
"""

from __future__ import annotations

import os
import re
import sys

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_ativo = False


def configurar(cor: bool | None = None) -> None:
    global _ativo
    if cor is None:
        cor = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    _ativo = cor
    if cor and os.name == "nt":
        os.system("")  # habilita sequências ANSI no console do Windows


def _c(codigo: str):
    def f(texto: str) -> str:
        return f"\x1b[{codigo}m{texto}\x1b[0m" if _ativo else texto
    return f


negrito = _c("1")
fraco = _c("2")
invertido = _c("7")
vermelho = _c("31")
verde = _c("32")
amarelo = _c("33")
azul = _c("34")
magenta = _c("35")
ciano = _c("36")
laranja = _c("38;5;208")
azul_claro = _c("38;5;75")
cinza = _c("90")
fundo_verde = _c("1;97;42")
fundo_vermelho = _c("1;97;41")
fundo_amarelo = _c("1;30;43")
cabeca = _c("1;30;48;5;214")  # célula/símbolo sob o cabeçote


def destaque(c: str) -> str:
    """Símbolo sob o cabeçote / próximo a ser lido: fundo colorido, ou [c] sem cores."""
    return cabeca(c) if _ativo else f"[{c}]"


def largura(s: str) -> int:
    return len(_ANSI.sub("", s))


def pad(s: str, n: int, alinhar: str = "<") -> str:
    falta = max(0, n - largura(s))
    if alinhar == ">":
        return " " * falta + s
    if alinhar == "^":
        return " " * (falta // 2) + s + " " * (falta - falta // 2)
    return s + " " * falta


def tabela(cabecalho: list[str], linhas: list[list[str] | None], alinhar: str | None = None) -> str:
    """Tabela com bordas. Uma linha None vira um separador horizontal."""
    alinhar = alinhar or "<" * len(cabecalho)
    n = len(cabecalho)
    larg = [largura(h) for h in cabecalho]
    for ln in linhas:
        if ln is not None:
            for i in range(n):
                larg[i] = max(larg[i], largura(ln[i]))

    def borda(e, m, d):
        return cinza(e + m.join("─" * (w + 2) for w in larg) + d)

    def linha(cels):
        sep = cinza("│")
        return sep + sep.join(" " + pad(c, larg[i], alinhar[i]) + " " for i, c in enumerate(cels)) + sep

    out = [borda("┌", "┬", "┐"), linha([negrito(h) for h in cabecalho]), borda("├", "┼", "┤")]
    for ln in linhas:
        out.append(borda("├", "┼", "┤") if ln is None else linha(ln))
    out.append(borda("└", "┴", "┘"))
    return "\n".join(out)


def caixa(texto: str, cor=None, largura_min: int = 0) -> str:
    linhas = texto.split("\n")
    w = max([largura_min] + [largura(x) for x in linhas])
    cor = cor or (lambda s: s)
    out = [cor("╭" + "─" * (w + 2) + "╮")]
    out += [cor("│") + " " + pad(x, w) + " " + cor("│") for x in linhas]
    out.append(cor("╰" + "─" * (w + 2) + "╯"))
    return "\n".join(out)


def titulo_etapa(texto: str, cor=None) -> str:
    cor = cor or negrito
    return "\n" + cor("▶ " + texto)


def selo(aceita: bool) -> str:
    return fundo_verde(" ✔ ACEITA ") if aceita else fundo_vermelho(" ✘ REJEITA ")
