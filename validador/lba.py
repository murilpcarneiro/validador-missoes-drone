"""Autômato linearmente limitado (ALL) determinístico genérico e o ALL do projeto.

Linguagem reconhecida pelo ALL do projeto (conferência dos comprovantes):

    L_ALL = { u = u  :  u ∈ {p,g}+ }

Para uma entrada de n símbolos a fita tem exatamente n + 2 células:
o marcador esquerdo '<', as n células graváveis e o marcador direito '>'.
Os marcadores podem ser lidos, nunca sobrescritos, e o cabeçote nunca
ultrapassa nenhum deles.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ESQ, DIR = "<", ">"  # marcadores de borda fixos


@dataclass(frozen=True)
class TransicaoALL:
    origem: str
    le: str
    destino: str
    escreve: str
    move: str  # 'E' (esquerda), 'D' (direita) ou 'P' (permanece)

    def __str__(self) -> str:
        return f"δ({self.origem}, {self.le}) = ({self.destino}, {self.escreve}, {self.move})"


@dataclass
class PassoALL:
    passo: int
    estado: str
    fita: str
    cabecote: int  # índice na fita (0 = marcador '<')
    transicao: TransicaoALL | None

    def fita_com_cabecote(self) -> str:
        return "".join(f"[{c}]" if i == self.cabecote else c for i, c in enumerate(self.fita))


@dataclass
class ResultadoALL:
    aceita: bool
    motivo: str
    rastro: list[PassoALL] = field(default_factory=list)


class LimiteFitaError(Exception):
    pass


class AutomatoLinearmenteLimitado:
    def __init__(self, estados, alfabeto, alfabeto_fita, transicoes, inicial,
                 aceitacao, rejeicao, dicas=None):
        self.estados = list(estados)
        self.alfabeto = set(alfabeto)
        self.alfabeto_fita = set(alfabeto_fita)
        self.inicial = inicial
        self.aceitacao = aceitacao
        self.rejeicao = rejeicao
        self.dicas = dicas or {}
        self.delta: dict[tuple[str, str], TransicaoALL] = {}
        for t in transicoes:
            chave = (t.origem, t.le)
            if chave in self.delta:
                raise ValueError(f"ALL não determinístico em {chave}")
            self._validar(t)
            self.delta[chave] = t

    def _validar(self, t: TransicaoALL) -> None:
        assert t.origem in self.estados and t.destino in self.estados, t
        assert t.le in self.alfabeto_fita and t.escreve in self.alfabeto_fita, t
        assert t.origem not in (self.aceitacao, self.rejeicao), t
        # marcadores: não podem ser sobrescritos nem ultrapassados
        if t.le in (ESQ, DIR) or t.escreve in (ESQ, DIR):
            if t.le != t.escreve:
                raise LimiteFitaError(f"{t} sobrescreve/cria marcador de borda")
        if t.le == ESQ and t.move == "E":
            raise LimiteFitaError(f"{t} ultrapassaria o marcador esquerdo")
        if t.le == DIR and t.move == "D":
            raise LimiteFitaError(f"{t} ultrapassaria o marcador direito")

    def executar(self, entrada: str) -> ResultadoALL:
        fita = [ESQ] + list(entrada) + [DIR]  # n + 2 células, nunca cresce
        estado, cab = self.inicial, 0
        rastro = [PassoALL(0, estado, "".join(fita), cab, None)]
        vistos = set()
        while estado not in (self.aceitacao, self.rejeicao):
            config = (estado, cab, "".join(fita))
            if config in vistos:  # impossível p/ este ALL; proteção genérica
                return ResultadoALL(False, "configuração repetida (laço) — rejeitado", rastro)
            vistos.add(config)
            t = self.delta.get((estado, fita[cab]))
            if t is None:
                # transição ausente = ida implícita ao estado de rejeição
                dica = self.dicas.get((estado, fita[cab])) or self.dicas.get(estado, "")
                motivo = (f"sem transição para ({estado}, '{fita[cab]}') na célula {cab} "
                          f"→ {self.rejeicao}" + (f": {dica}" if dica else ""))
                estado = self.rejeicao
                rastro.append(PassoALL(len(rastro), estado, "".join(fita), cab, None))
                return ResultadoALL(False, motivo, rastro)
            fita[cab] = t.escreve
            cab += {"E": -1, "D": 1, "P": 0}[t.move]
            if not 0 <= cab < len(fita):  # garantido pela validação; checagem extra
                raise LimiteFitaError("cabeçote saiu da fita")
            estado = t.destino
            rastro.append(PassoALL(len(rastro), estado, "".join(fita), cab, t))
        if estado == self.aceitacao:
            return ResultadoALL(True, f"alcançou {self.aceitacao}: comprovantes conferem com o embarque", rastro)
        return ResultadoALL(False, f"alcançou {self.rejeicao}", rastro)


# --------------------------------------------------------------------------
# ALL do projeto
# --------------------------------------------------------------------------
SIGMA_ALL = {"p", "g", "="}
GAMA_ALL = SIGMA_ALL | {"X", "Y", ESQ, DIR}


def _construir_all() -> AutomatoLinearmenteLimitado:
    T = TransicaoALL
    d = [
        # q0: cabeçote sobre '<'; entra na primeira célula gravável
        T("q0", ESQ, "q1", ESQ, "D"),
        # q1: primeiro volume (u não pode ser vazio): marca com X e memoriza o tipo
        T("q1", "p", "q2", "X", "D"),
        T("q1", "g", "q3", "X", "D"),
        # q2 / q3: levando 'p' / 'g' para a direita até o '='
        T("q2", "p", "q2", "p", "D"), T("q2", "g", "q2", "g", "D"), T("q2", "=", "q4", "=", "D"),
        T("q3", "p", "q3", "p", "D"), T("q3", "g", "q3", "g", "D"), T("q3", "=", "q5", "=", "D"),
        # q4 / q5: pula comprovantes já conferidos (Y) e confere o próximo
        T("q4", "Y", "q4", "Y", "D"), T("q4", "p", "q6", "Y", "E"),
        T("q5", "Y", "q5", "Y", "D"), T("q5", "g", "q6", "Y", "E"),
        # q6: volta para a esquerda até o último X
        T("q6", "p", "q6", "p", "E"), T("q6", "g", "q6", "g", "E"),
        T("q6", "=", "q6", "=", "E"), T("q6", "Y", "q6", "Y", "E"),
        T("q6", "X", "q7", "X", "D"),
        # q7: próximo volume não conferido, ou '=' se todos já foram marcados
        T("q7", "p", "q2", "X", "D"), T("q7", "g", "q3", "X", "D"), T("q7", "=", "q8", "=", "D"),
        # q8: todos os comprovantes devem estar marcados até o '>'
        T("q8", "Y", "q8", "Y", "D"), T("q8", DIR, "qA", DIR, "P"),
    ]
    dicas = {
        ("q1", "="): "não há volumes embarcados antes do '='",
        ("q1", DIR): "entrada vazia",
        ("q2", DIR): "falta o separador '='",
        ("q3", DIR): "falta o separador '='",
        ("q4", "g"): "comprovante 'g' onde o embarque exigia 'p' (ordem/tipo diferente)",
        ("q5", "p"): "comprovante 'p' onde o embarque exigia 'g' (ordem/tipo diferente)",
        ("q4", DIR): "há menos comprovantes do que volumes",
        ("q5", DIR): "há menos comprovantes do que volumes",
        ("q4", "="): "mais de um separador '='",
        ("q5", "="): "mais de um separador '='",
        ("q8", "p"): "há mais comprovantes do que volumes",
        ("q8", "g"): "há mais comprovantes do que volumes",
        ("q8", "="): "mais de um separador '='",
    }
    return AutomatoLinearmenteLimitado(
        estados=[f"q{i}" for i in range(9)] + ["qA", "qR"],
        alfabeto=SIGMA_ALL,
        alfabeto_fita=GAMA_ALL,
        transicoes=d,
        inicial="q0",
        aceitacao="qA",
        rejeicao="qR",
        dicas=dicas,
    )


ALL_COMPROVANTES = _construir_all()
