"""Executa os testes obrigatórios e grava o registro em tests/RESULTADOS.md.

Uso:  py tests/executar_testes.py
Para cada teste registra: entrada, decisão esperada, decisão obtida e regra verificada.
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from validador import estilo as E  # noqa: E402
from validador.__main__ import colorir_entrada, main as cli_main  # noqa: E402
from validador.pipeline import executar_all, executar_ap, executar_fluxo  # noqa: E402

PASTA = Path(__file__).resolve().parent
COMPRIMENTO_MINIMO = 18


def carregar(nome):
    return json.loads((PASTA / nome).read_text(encoding="utf-8"))


def dec(b: bool) -> str:
    return "aceita" if b else "rejeita"


def esc(s: str) -> str:
    return s.replace("|", r"\|")


def md(s: str) -> str:
    return f"`{s}`" if s else "*(vazia)*"


def testar_modulo(arquivo, executar, linhas, falhas):
    dados = carregar(arquivo)
    casos = dados["casos"]
    entradas = [c["entrada"] for c in casos]
    assert len(set(entradas)) == len(entradas), f"{arquivo}: cadeias repetidas"
    n_ac = sum(c["esperado"] == "aceita" for c in casos)
    n_rj = len(casos) - n_ac
    assert n_ac >= 8 and n_rj >= 8, f"{arquivo}: mínimo de 8 aceitas e 8 rejeitadas"
    assert any(c.get("limite") for c in casos), f"{arquivo}: falta caso-limite"

    linhas.append(f"\n## Módulo {dados['modulo']} ({n_ac} aceitas, {n_rj} rejeitadas)\n")
    linhas.append("| # | Entrada | Tam. | Esperado | Obtido | OK | Regra verificada | Motivo informado pelo autômato |")
    linhas.append("|---|---|---|---|---|---|---|---|")
    tela = []
    for i, c in enumerate(casos, 1):
        if not c.get("limite"):
            assert len(c["entrada"]) >= COMPRIMENTO_MINIMO, f"{c['entrada']}: menos de 18 símbolos"
        r = executar(c["entrada"])
        obtido = dec(r.aceita)
        ok = obtido == c["esperado"]
        if not ok:
            falhas.append(f"{dados['modulo']} #{i} {c['entrada']!r}: esperado {c['esperado']}, obtido {obtido}")
        linhas.append(f"| {i} | {md(c['entrada'])} | {len(c['entrada'])} | {c['esperado']} | {obtido} | "
                      f"{'✅' if ok else '❌'} | {esc(c['regra'])} | {esc(r.motivo)} |")
        tela.append([str(i), colorir_entrada(c["entrada"]) or E.cinza("(vazia)"), c["esperado"],
                     (E.verde if r.aceita else E.vermelho)(obtido),
                     E.verde("✔") if ok else E.vermelho("✘"), E.cinza(c["regra"])])
    print(E.titulo_etapa(f"Módulo {dados['modulo']} · {n_ac} aceitas, {len(casos) - n_ac} rejeitadas",
                         E.laranja if dados["modulo"] == "AP" else E.azul_claro))
    print(E.tabela(["#", "entrada", "esperado", "obtido", "ok", "regra verificada"], tela, "><<<^<"))


def testar_integracao(linhas, falhas):
    dados = carregar("casos_integracao.json")
    linhas.append("\n## Fluxo completo (integração AP → ALL)\n")
    tela = []
    linhas.append("| # | Entrada | Tam. | Esperado AP | Obtido AP | Esperado ALL | Obtido ALL | OK | Regra verificada |")
    linhas.append("|---|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(dados["casos"], 1):
        f = executar_fluxo(c["entrada"])
        ob_ap = dec(f.ap.aceita)
        ob_all = "nao_executado" if f.all is None else dec(f.all.aceita)
        ok = ob_ap == c["esperado_ap"] and ob_all == c["esperado_all"]
        if not ok:
            falhas.append(f"Integração #{i} {c['entrada']!r}: obtido {ob_ap}/{ob_all}")
        linhas.append(f"| {i} | {md(c['entrada'])} | {len(c['entrada'])} | {c['esperado_ap']} | {ob_ap} | "
                      f"{c['esperado_all']} | {ob_all} | {'✅' if ok else '❌'} | {esc(c['regra'])} |")
        tela.append([str(i), colorir_entrada(c["entrada"]), ob_ap, ob_all.replace("nao_executado", "não executado"),
                     E.verde("✔") if ok else E.vermelho("✘"), E.cinza(c["regra"])])
    print(E.titulo_etapa("Fluxo completo (integração AP → ALL)"))
    print(E.tabela(["#", "entrada", "AP", "ALL", "ok", "regra verificada"], tela, "><<<^<"))

    linhas.append("\n## Símbolo fora do alfabeto de entrada\n")
    print(E.titulo_etapa("Símbolo fora do alfabeto de entrada"))
    for c in dados["simbolo_invalido"]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            codigo = cli_main(["-m", c["modulo"], c["entrada"]])
        E.configurar()  # a CLI reconfigurou as cores para o buffer; volta ao terminal
        msg = buf.getvalue().strip()
        print(f"  {E.cinza('$ py -m validador -m ' + c['modulo'] + ' ' + c['entrada'])}\n  {E.vermelho(msg)}")
        if codigo != 2 or "não pertence ao alfabeto" not in msg:
            falhas.append(f"Símbolo inválido {c['entrada']!r}: mensagem inesperada")
        linhas.append(f"Comando: `py -m validador -m {c['modulo']} \"{c['entrada']}\"` (código de saída {codigo})\n")
        linhas.append(f"```\n{msg}\n```\n")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    linhas = ["# Resultados dos testes obrigatórios",
              "", "Gerado automaticamente por `py tests/executar_testes.py`.",
              f"Cadeias regulares de teste têm no mínimo {COMPRIMENTO_MINIMO} símbolos; "
              "as marcadas como CASO-LIMITE são exceções propositais."]
    E.configurar()
    falhas: list[str] = []
    testar_modulo("casos_ap.json", executar_ap, linhas, falhas)
    testar_modulo("casos_all.json", executar_all, linhas, falhas)
    testar_integracao(linhas, falhas)
    linhas.append("\n## Resumo\n")
    linhas.append("Todos os testes passaram." if not falhas else "Falhas:\n" + "\n".join(f"- {x}" for x in falhas))
    texto = "\n".join(linhas) + "\n"
    (PASTA / "RESULTADOS.md").write_text(texto, encoding="utf-8")
    if falhas:
        print("\n" + E.caixa(E.vermelho(E.negrito(f"{len(falhas)} FALHA(S)")) + "\n" + "\n".join(falhas), E.vermelho))
    else:
        print("\n" + E.caixa(E.verde(E.negrito("✔ Todos os testes passaram")) + "\n"
                             + E.cinza("Registro completo em tests/RESULTADOS.md"), E.verde))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
