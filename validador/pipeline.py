"""Fluxo em duas etapas: AP (estrutura) → ALL (dependência sensível ao contexto)."""

from __future__ import annotations

from dataclasses import dataclass

from .ap import AP_MISSAO, SIGMA_AP, ResultadoAP
from .lba import ALL_COMPROVANTES, SIGMA_ALL, ResultadoALL


class SimboloInvalido(ValueError):
    pass


def verificar_alfabeto(entrada: str, alfabeto: set[str], modulo: str) -> None:
    for i, c in enumerate(entrada):
        if c not in alfabeto:
            simbolos = ", ".join(sorted(alfabeto))
            raise SimboloInvalido(
                f"ERRO ({modulo}): símbolo '{c}' na posição {i} não pertence ao "
                f"alfabeto de entrada Σ = {{{simbolos}}}. Nenhum autômato foi executado."
            )


def executar_ap(entrada: str) -> ResultadoAP:
    verificar_alfabeto(entrada, SIGMA_AP, "AP")
    return AP_MISSAO.executar(entrada)


def executar_all(entrada: str) -> ResultadoALL:
    verificar_alfabeto(entrada, SIGMA_ALL, "ALL")
    return ALL_COMPROVANTES.executar(entrada)


@dataclass
class ResultadoFluxo:
    entrada: str
    ap: ResultadoAP
    trecho_all: str | None
    all: ResultadoALL | None

    @property
    def aceita(self) -> bool:
        return self.ap.aceita and self.all is not None and self.all.aceita

    @property
    def decisao(self) -> str:
        if not self.ap.aceita:
            return "REJEITADA pelo AP (ALL não executado)"
        if not self.all.aceita:
            return "aceita pelo AP, REJEITADA pelo ALL"
        return "ACEITA (AP e ALL)"


def executar_fluxo(entrada: str) -> ResultadoFluxo:
    ap = executar_ap(entrada)
    if not ap.aceita:
        return ResultadoFluxo(entrada, ap, None, None)
    trecho = entrada.split("#", 1)[1]  # o ALL recebe o trecho após '#'
    return ResultadoFluxo(entrada, ap, trecho, executar_all(trecho))
