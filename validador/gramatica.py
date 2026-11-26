"""GLC que gera L_AP e construção da derivação mais à esquerda.

G = (V, Σ, P, M)
  V = {M, R, C, T}
  Σ = {N, S, L, O, *, #, p, g, =}
  P:
    M → R # C
    R → N R S | S R N | L R O | O R L
      | N * S | S * N | L * O | O * L
    C → T C T | T = T
    T → p | g
"""

from __future__ import annotations

from .ap import INVERSO

PRODUCOES = [
    ("M", "R # C"),
    ("R", "N R S | S R N | L R O | O R L | N * S | S * N | L * O | O * L"),
    ("C", "T C T | T = T"),
    ("T", "p | g"),
]
NAO_TERMINAIS = {"M", "R", "C", "T"}


class NaoDerivavel(ValueError):
    pass


def _arvore(cadeia: str):
    """Constrói a árvore sintática (G é não ambígua) ou levanta NaoDerivavel."""
    if cadeia.count("#") != 1:
        raise NaoDerivavel("a cadeia deve conter exatamente um '#'")
    rota, carga = cadeia.split("#")
    if rota.count("*") != 1 or carga.count("=") != 1:
        raise NaoDerivavel("rota precisa de um '*' e carga de um '='")
    ida, volta = rota.split("*")
    u, v = carga.split("=")
    if not ida or len(ida) != len(volta):
        raise NaoDerivavel("ida vazia ou ida/volta com tamanhos diferentes")
    k = len(ida)
    for i in range(k):  # par externo de R → x R inv(x)
        if ida[i] not in INVERSO or volta[k - 1 - i] != INVERSO[ida[i]]:
            raise NaoDerivavel(f"movimento {i + 1} da ida não casa com a volta")
    if not u or len(u) != len(v) or any(c not in "pg" for c in u + v):
        raise NaoDerivavel("volumes/comprovantes vazios, inválidos ou em quantidades diferentes")

    def R(i):
        if i == k - 1:
            return ("R", [ida[i], "*", volta[k - 1 - i]])
        return ("R", [ida[i], R(i + 1), volta[k - 1 - i]])

    m = len(u)

    def C(i):
        if i == m - 1:
            return ("C", [("T", [u[i]]), "=", ("T", [v[m - 1 - i]])])
        return ("C", [("T", [u[i]]), C(i + 1), ("T", [v[m - 1 - i]])])

    return ("M", [R(0), "#", C(0)])


def pertence(cadeia: str) -> bool:
    try:
        _arvore(cadeia)
        return True
    except NaoDerivavel:
        return False


def derivacao_mais_a_esquerda(cadeia: str) -> list[tuple[str, str]]:
    """Retorna [(forma sentencial, produção aplicada para chegar nela), ...]."""
    forma = [_arvore(cadeia)]
    passos = [("M", "")]

    def texto(f):
        return "".join(x if isinstance(x, str) else x[0] for x in f)

    while True:
        idx = next((i for i, x in enumerate(forma) if not isinstance(x, str)), None)
        if idx is None:
            break
        nt, filhos = forma[idx]
        producao = f"{nt} → " + " ".join(f if isinstance(f, str) else f[0] for f in filhos)
        forma = forma[:idx] + filhos + forma[idx + 1:]
        passos.append((texto(forma), producao))
    assert passos[-1][0] == cadeia
    return passos
