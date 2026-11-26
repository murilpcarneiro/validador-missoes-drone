"""Interface de linha de comando.

Exemplos:
    py -m validador "NNLLN*SOOSS#ppgp=ppgp"          fluxo completo
    py -m validador -t "NNLLN*SOOSS#ppgp=ppgp"       fluxo com rastreamento
    py -m validador -m ap -t "N*S#p=p"               só o AP
    py -m validador -m all -t "pgp=pgp"              só o ALL
    py -m validador -d "NNLLN*SOOSS#ppgp=ppgp"       derivação mais à esquerda
    py -m validador --demo                           três cenários de integração
    py -m validador --spec                           especificação formal
    py -m validador -a exemplos/entradas.txt         valida um arquivo de entradas
    py -m validador                                  modo interativo
"""

from __future__ import annotations

import argparse
import sys

from . import estilo as E
from . import gramatica
from .ap import AP_MISSAO, GAMA_AP, SIGMA_AP, ResultadoAP
from .lba import ALL_COMPROVANTES, GAMA_ALL, SIGMA_ALL, ResultadoALL
from .pipeline import SimboloInvalido, executar_all, executar_ap, executar_fluxo

CENARIOS_DEMO = [
    ("Aceita pelos dois módulos", "NNLLN*SOOSS#ppgp=ppgp"),
    ("Rejeitada pelo AP (volta não desfaz a ida)", "NNLLN*SOSOS#ppgp=ppgp"),
    ("Aceita pelo AP e rejeitada pelo ALL (ordem dos comprovantes)", "NNLLN*SOOSS#ppgp=pgpp"),
]


def _trans_ap(t) -> str:
    if t is None:
        return E.cinza("configuração inicial")
    s = "ε" if t.simbolo is None else t.simbolo
    return E.cinza(f"δ({t.origem}, {s}, {t.topo}) → ({t.destino}, {t.empilha or 'ε'})")


def _entrada_ap(texto: str, pos: int) -> str:
    feito, resto = texto[:pos], texto[pos:]
    if not resto:
        return E.cinza(feito) + E.destaque("ε")
    return E.cinza(feito) + E.destaque(resto[0]) + resto[1:]


def _pilha(pilha: str) -> str:
    if pilha.startswith("$"):
        return E.cinza("$")
    return E.amarelo(E.negrito(pilha[0])) + E.amarelo(pilha[1:-1]) + E.cinza("$")


def imprimir_rastro_ap(r: ResultadoAP, entrada: str | None = None) -> None:
    entrada = entrada if entrada is not None else r.rastro[0].restante
    linhas = []
    for p in r.rastro:
        linhas.append([str(p.passo), E.ciano(p.estado), str(p.posicao), _entrada_ap(entrada, p.posicao),
                       _pilha(p.pilha), _trans_ap(p.transicao)])
    print(E.tabela(["passo", "estado", "pos", "entrada (▸ símbolo lido)", "pilha (topo ←)", "transição"],
                   linhas, ">^><<<"))


def _celula(c: str) -> str:
    if c in "<>":
        return E.cinza(c)
    if c == "X":
        return E.laranja(c)
    if c == "Y":
        return E.azul_claro(c)
    return c


def _fita(fita: str, cab: int) -> str:
    return "".join(E.destaque(c) if i == cab else _celula(c) for i, c in enumerate(fita))


def imprimir_rastro_all(r: ResultadoALL) -> None:
    linhas = []
    for p in r.rastro:
        if p.estado == "q7":  # início de uma nova rodada de conferência
            linhas.append(None)
        if p.transicao:
            t = p.transicao
            trans = E.cinza(f"δ({t.origem}, {t.le}) → ({t.destino}, {t.escreve}, {t.move})")
        else:
            trans = E.cinza("configuração inicial") if p.passo == 0 else E.vermelho("sem transição → qR")
        est = E.verde(p.estado) if p.estado == "qA" else E.vermelho(p.estado) if p.estado == "qR" else E.ciano(p.estado)
        linhas.append([str(p.passo), est, str(p.cabecote), _fita(p.fita, p.cabecote), trans])
    print(E.tabela(["passo", "estado", "cab", "fita (▸ cabeçote)", "transição"], linhas, ">^><<"))
    print(E.cinza("  X = volume conferido · Y = comprovante conferido · < > = marcadores de borda · "
                  "linhas horizontais separam as rodadas"))


def colorir_entrada(s: str) -> str:
    out = []
    for c in s:
        if c in "NSLO":
            out.append(E.laranja(c))
        elif c in "pg":
            out.append(E.azul_claro(c))
        elif c in "*#=":
            out.append(E.negrito(c))
        else:
            out.append(E.vermelho(c))
    return "".join(out)


def _decisao(nome: str, aceita: bool, motivo: str) -> None:
    print(f"\n  {E.negrito(nome)} {E.selo(aceita)}  {motivo}")


def rodar_ap(entrada: str, rastro: bool) -> None:
    r = executar_ap(entrada)
    print(E.titulo_etapa(f"AP · entrada {colorir_entrada(entrada)} ({len(entrada)} símbolos)", E.laranja))
    if rastro:
        imprimir_rastro_ap(r, entrada)
    _decisao("AP", r.aceita, r.motivo)


def rodar_all(entrada: str, rastro: bool) -> None:
    r = executar_all(entrada)
    print(E.titulo_etapa(f"ALL · entrada {colorir_entrada(entrada)} "
                         f"(n = {len(entrada)}; fita = {len(entrada) + 2} células)", E.azul_claro))
    if rastro:
        imprimir_rastro_all(r)
    _decisao("ALL", r.aceita, r.motivo)


def rodar_fluxo(entrada: str, rastro: bool, titulo: str | None = None) -> None:
    f = executar_fluxo(entrada)
    cab = (E.negrito(titulo) + "\n" if titulo else "") + f"Entrada: {colorir_entrada(entrada)}  {E.cinza(f'({len(entrada)} símbolos)')}"
    print("\n" + E.caixa(cab, E.cinza, 60))

    print(E.titulo_etapa("Etapa 1 · AP — estrutura da missão (rota espelhada e contagem)", E.laranja))
    if rastro:
        imprimir_rastro_ap(f.ap, entrada)
    _decisao("AP", f.ap.aceita, f.ap.motivo)

    if f.all is None:
        print(E.titulo_etapa("Etapa 2 · ALL — conferência dos comprovantes", E.azul_claro))
        print(f"\n  {E.negrito('ALL')} {E.fundo_amarelo(' — NÃO EXECUTADO ')}  a entrada foi rejeitada pelo AP")
    else:
        t = f.trecho_all
        print(E.titulo_etapa(f"Etapa 2 · ALL — conferência dos comprovantes · trecho após '#': "
                             f"{colorir_entrada(t)} (n = {len(t)}; fita = {len(t) + 2} células)", E.azul_claro))
        if rastro:
            imprimir_rastro_all(f.all)
        _decisao("ALL", f.all.aceita, f.all.motivo)

    cor = E.verde if f.aceita else E.vermelho
    print("\n" + E.caixa(E.negrito("RESULTADO FINAL: ") + cor(E.negrito(f.decisao)), cor))


def rodar_derivacao(entrada: str) -> None:
    print(E.titulo_etapa(f"Derivação mais à esquerda de {colorir_entrada(entrada)}", E.laranja))
    try:
        passos = gramatica.derivacao_mais_a_esquerda(entrada)
    except gramatica.NaoDerivavel as e:
        print(f"  {E.selo(False)}  a cadeia não pertence a L(G): {e}")
        return
    larg = max(len(f) for f, _ in passos)
    for i, (forma, prod) in enumerate(passos):
        seta = "   " if i == 0 else E.cinza(" ⇒ ")
        txt = "".join(E.magenta(E.negrito(c)) if c in gramatica.NAO_TERMINAIS else colorir_entrada(c) for c in forma)
        print(f"  {E.cinza(f'{i:>2}')}{seta}{E.pad(txt, larg)}   {E.cinza(prod)}")


def imprimir_spec() -> None:
    print("=== GLC G = (V, Σ, P, M) ===")
    print("V = {M, R, C, T}; Σ =", "{" + ", ".join(sorted(SIGMA_AP)) + "}; símbolo inicial: M")
    for nt, corpo in gramatica.PRODUCOES:
        print(f"  {nt} → {corpo}")
    print("\n=== AP (aceitação por estado final, entrada consumida por inteiro) ===")
    print("Q =", AP_MISSAO.estados, "| q0 inicial | F =", sorted(AP_MISSAO.finais))
    print("Σ =", "{" + ", ".join(sorted(SIGMA_AP)) + "}", "| Γ =", "{" + ", ".join(sorted(GAMA_AP)) + "}",
          "| fundo da pilha: $")
    for t in AP_MISSAO.transicoes:
        print("  ", t)
    print(f"Total: {len(AP_MISSAO.transicoes)} transições")
    print("\n=== ALL (transição ausente → qR) ===")
    print("Q =", ALL_COMPROVANTES.estados, "| inicial q0 | aceitação qA | rejeição qR")
    print("Σ =", "{" + ", ".join(sorted(SIGMA_ALL)) + "}", "| Γ =", "{" + ", ".join(sorted(GAMA_ALL)) + "}",
          "| marcadores: < e >")
    for t in ALL_COMPROVANTES.delta.values():
        print("  ", t)
    print(f"Total: {len(ALL_COMPROVANTES.delta)} transições")


def demo() -> None:
    for i, (titulo, cadeia) in enumerate(CENARIOS_DEMO, 1):
        rodar_fluxo(cadeia, rastro=True, titulo=f"CENÁRIO {i} · {titulo}")
        print()
    rodar_derivacao(CENARIOS_DEMO[0][1])


def interativo() -> None:
    print(E.caixa(E.negrito("Validador de missões de drone · AP + ALL") + "\n"
                  "Digite uma cadeia para o fluxo completo (ou 'sair').\n"
                  + E.cinza("Prefixos: ap:  all:  der:   ·   sufixo -t: rastreamento"), E.cinza))
    while True:
        try:
            linha = input("\n" + E.negrito("› ")).strip()
        except EOFError:
            break
        if linha.lower() in {"sair", "exit", "q"}:
            break
        rastro = linha.endswith(" -t")
        if rastro:
            linha = linha[:-3].strip()
        try:
            if linha.startswith("ap:"):
                rodar_ap(linha[3:].strip(), rastro)
            elif linha.startswith("all:"):
                rodar_all(linha[4:].strip(), rastro)
            elif linha.startswith("der:"):
                rodar_derivacao(linha[4:].strip())
            else:
                rodar_fluxo(linha, rastro)
        except SimboloInvalido as e:
            print(E.vermelho(str(e)))


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:  # pragma: no cover
            pass
    ap = argparse.ArgumentParser(prog="validador", description="AP + ALL para missões de drone")
    ap.add_argument("entrada", nargs="?", help="cadeia a validar")
    ap.add_argument("-m", "--modulo", choices=["fluxo", "ap", "all"], default="fluxo")
    ap.add_argument("-t", "--trace", action="store_true", help="mostra o rastreamento")
    ap.add_argument("-d", "--derivacao", action="store_true", help="mostra a derivação na GLC")
    ap.add_argument("--demo", action="store_true", help="executa os três cenários de integração")
    ap.add_argument("--spec", action="store_true", help="imprime GLC, AP e ALL")
    ap.add_argument("--sem-cor", action="store_true", help="desliga as cores")
    ap.add_argument("-a", "--arquivo", help="valida cada linha de um arquivo (linhas '# ...' são comentários)")
    args = ap.parse_args(argv)
    E.configurar(False if args.sem_cor else None)

    if args.spec:
        imprimir_spec()
        return 0
    if args.demo:
        demo()
        return 0
    if args.arquivo:
        with open(args.arquivo, encoding="utf-8") as fh:
            for linha in fh:
                linha = linha.strip()
                if not linha or linha.startswith("# "):
                    continue
                try:
                    rodar_fluxo(linha, args.trace)
                except SimboloInvalido as e:
                    print(f"\nEntrada '{linha}':\n{e}")
        return 0
    if args.entrada is None:
        interativo()
        return 0
    try:
        if args.derivacao:
            rodar_derivacao(args.entrada)
        elif args.modulo == "ap":
            rodar_ap(args.entrada, args.trace)
        elif args.modulo == "all":
            rodar_all(args.entrada, args.trace)
        else:
            rodar_fluxo(args.entrada, args.trace)
    except SimboloInvalido as e:
        print(E.vermelho(str(e)))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
