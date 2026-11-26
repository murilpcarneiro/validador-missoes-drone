"""Autômato de pilha (AP) determinístico genérico e o AP do projeto.

Linguagem reconhecida pelo AP do projeto (validador de missões de drone):

    L_AP = { w * inv(w)^R # u = v  :  w ∈ {N,S,L,O}+,  u, v ∈ {p,g}+,  |u| = |v| }

onde inv troca N<->S e L<->O.  Aceitação por ESTADO FINAL com a entrada
consumida por inteiro.
"""

from __future__ import annotations

from dataclasses import dataclass, field

EPS = None  # representa ε (transição que não consome entrada)
FUNDO = "$"  # marcador de fundo da pilha (Z0)


@dataclass(frozen=True)
class TransicaoAP:
    origem: str
    simbolo: str | None  # None = ε
    topo: str  # símbolo desempilhado (o AP sempre lê o topo)
    destino: str
    empilha: str  # string empilhada; o 1º caractere vira o novo topo ("" = só desempilha)

    def __str__(self) -> str:
        s = "ε" if self.simbolo is None else self.simbolo
        e = self.empilha if self.empilha else "ε"
        return f"δ({self.origem}, {s}, {self.topo}) = ({self.destino}, {e})"


@dataclass
class PassoAP:
    passo: int
    estado: str
    posicao: int  # índice (0-based) do próximo símbolo a ser lido
    restante: str
    pilha: str  # topo à esquerda
    transicao: TransicaoAP | None  # transição que LEVOU a esta configuração


@dataclass
class ResultadoAP:
    aceita: bool
    motivo: str
    rastro: list[PassoAP] = field(default_factory=list)


class NaoDeterminismoError(Exception):
    pass


class AutomatoPilha:
    """AP determinístico. A determinismo é verificado na construção."""

    def __init__(self, estados, alfabeto, alfabeto_pilha, transicoes, inicial, finais,
                 dicas=None):
        self.estados = list(estados)
        self.alfabeto = set(alfabeto)
        self.alfabeto_pilha = set(alfabeto_pilha)
        self.transicoes = list(transicoes)
        self.inicial = inicial
        self.finais = set(finais)
        self.dicas = dicas or {}
        self._validar()

    def _validar(self) -> None:
        for t in self.transicoes:
            assert t.origem in self.estados and t.destino in self.estados, t
            assert t.simbolo is None or t.simbolo in self.alfabeto, t
            assert t.topo in self.alfabeto_pilha, t
            assert all(c in self.alfabeto_pilha for c in t.empilha), t
        # Condição de determinismo (DPDA): para o mesmo (estado, topo) não pode
        # haver duas transições com o mesmo símbolo, nem uma ε junto com outra.
        for i, a in enumerate(self.transicoes):
            for b in self.transicoes[i + 1:]:
                if a.origem == b.origem and a.topo == b.topo and (
                    a.simbolo == b.simbolo or a.simbolo is None or b.simbolo is None
                ):
                    raise NaoDeterminismoError(f"conflito entre {a} e {b}")

    def _aplicavel(self, estado, simbolo, topo):
        for t in self.transicoes:
            if t.origem != estado or t.topo != topo:
                continue
            if t.simbolo is None or (simbolo is not None and t.simbolo == simbolo):
                return t
        return None

    def executar(self, entrada: str) -> ResultadoAP:
        estado, pos, pilha = self.inicial, 0, [FUNDO]  # topo = fim da lista
        n = len(entrada)

        def foto(k, t):
            return PassoAP(k, estado, pos, entrada[pos:], "".join(reversed(pilha)), t)

        rastro = [foto(0, None)]
        # Cada transição não-ε consome 1 símbolo; o AP do projeto tem apenas
        # duas transições ε e nenhuma delas forma ciclo. Limite de segurança:
        limite = 2 * n + 2 * len(self.estados) + 2
        while len(rastro) <= limite:
            simbolo = entrada[pos] if pos < n else None
            topo = pilha[-1] if pilha else None
            t = self._aplicavel(estado, simbolo, topo) if topo is not None else None
            if t is None:
                break
            pilha.pop()
            pilha.extend(reversed(t.empilha))
            estado = t.destino
            if t.simbolo is not None:
                pos += 1
            rastro.append(foto(len(rastro), t))
        else:  # pragma: no cover - não ocorre com o AP do projeto
            return ResultadoAP(False, "limite de passos excedido (laço de ε)", rastro)

        if estado in self.finais and pos == n:
            return ResultadoAP(True, f"entrada consumida e {estado} é estado final", rastro)
        if pos < n:
            topo = pilha[-1] if pilha else "∅"
            dica = self.dicas.get((estado, entrada[pos])) or self.dicas.get(estado, "")
            return ResultadoAP(
                False,
                f"sem transição para ({estado}, '{entrada[pos]}', topo {topo}) "
                f"na posição {pos}" + (f": {dica}" if dica else ""),
                rastro,
            )
        dica = self.dicas.get((estado, "fim")) or self.dicas.get(estado, "")
        return ResultadoAP(
            False,
            f"entrada consumida, mas {estado} não é estado final" + (f": {dica}" if dica else ""),
            rastro,
        )


# --------------------------------------------------------------------------
# AP do projeto
# --------------------------------------------------------------------------
DIRECOES = "NSLO"
INVERSO = {"N": "S", "S": "N", "L": "O", "O": "L"}
VOLUMES = "pg"
SIGMA_AP = set(DIRECOES) | set(VOLUMES) | {"*", "#", "="}
GAMA_AP = set(DIRECOES) | {"K", FUNDO}


def _construir_ap() -> AutomatoPilha:
    T = TransicaoAP
    d = []
    # q0: configura o fundo da pilha (ε, $ / $) e passa a ler a ida
    d.append(T("q0", EPS, FUNDO, "q1", FUNDO))
    # q1: primeiro movimento da ida (garante w não vazio)
    for x in DIRECOES:
        d.append(T("q1", x, FUNDO, "q2", x + FUNDO))
    # q2: demais movimentos da ida; '*' marca o ponto de entrega (retorno)
    for x in DIRECOES:
        for y in DIRECOES:
            d.append(T("q2", x, y, "q2", x + y))
    for y in DIRECOES:
        d.append(T("q2", "*", y, "q3", y))
    # q3: volta — cada movimento deve ser o inverso do topo
    for x in DIRECOES:
        d.append(T("q3", INVERSO[x], x, "q3", ""))
    d.append(T("q3", "#", FUNDO, "q4", FUNDO))
    # q4: primeiro volume embarcado (garante u não vazio)
    for v in VOLUMES:
        d.append(T("q4", v, FUNDO, "q5", "K" + FUNDO))
    # q5: demais volumes; '=' inicia os comprovantes
    for v in VOLUMES:
        d.append(T("q5", v, "K", "q5", "KK"))
    d.append(T("q5", "=", "K", "q6", "K"))
    # q6: cada comprovante desempilha um K; com $ no topo vai a q7
    for v in VOLUMES:
        d.append(T("q6", v, "K", "q6", ""))
    d.append(T("q6", EPS, FUNDO, "q7", FUNDO))

    dicas = {
        "q1": "a rota de ida deve começar com um movimento N, S, L ou O",
        "q2": "esperado movimento da ida ou '*' (ponto de entrega)",
        "q3": "a volta deve repetir a ida ao contrário com direções inversas, seguida de '#'",
        ("q3", "#"): "a volta é mais curta que a ida (ainda há movimentos na pilha)",
        ("q3", "fim"): "faltam a volta e/ou o manifesto de carga",
        "q4": "o manifesto deve começar com um volume p ou g",
        "q5": "esperado volume p/g ou '='",
        "q6": "há mais comprovantes do que volumes embarcados ou símbolo inválido",
        ("q6", "fim"): "há menos comprovantes do que volumes embarcados",
        "q7": "todos os volumes já foram comprovados, mas ainda há símbolos "
              "(comprovantes a mais ou símbolos excedentes)",
    }
    return AutomatoPilha(
        estados=[f"q{i}" for i in range(8)],
        alfabeto=SIGMA_AP,
        alfabeto_pilha=GAMA_AP,
        transicoes=d,
        inicial="q0",
        finais={"q7"},
        dicas=dicas,
    )


AP_MISSAO = _construir_ap()
