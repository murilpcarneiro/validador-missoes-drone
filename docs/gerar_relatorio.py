"""Gera docs/relatorio.html (e docs/relatorio.pdf, se o Microsoft Edge ou o Chrome estiverem instalados).

Rastreamentos, derivação, diagramas e tabelas de teste são produzidos a partir da
execução real do código, para que o relatório nunca divirja da implementação.

Uso:  py docs/gerar_relatorio.py
"""

from __future__ import annotations

import html
import io
import json
import math
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

DOCS = Path(__file__).resolve().parent
RAIZ = DOCS.parent
sys.path.insert(0, str(RAIZ))

from validador import gramatica  # noqa: E402
from validador.__main__ import imprimir_rastro_ap, imprimir_rastro_all, main as cli_main  # noqa: E402
from validador.pipeline import executar_all, executar_ap, executar_fluxo  # noqa: E402

R = 24  # raio dos estados
COR = "#1f4e79"


# ----------------------------------------------------------------- SVG helpers
def estado(x, y, nome, final=False, inicial=False):
    s = f'<circle cx="{x}" cy="{y}" r="{R}" fill="#fff" stroke="{COR}" stroke-width="2"/>'
    if final:
        s += f'<circle cx="{x}" cy="{y}" r="{R - 5}" fill="none" stroke="{COR}" stroke-width="1.5"/>'
    s += f'<text x="{x}" y="{y + 5}" text-anchor="middle" font-size="14" font-weight="bold">{nome}</text>'
    if inicial:
        s += seta_reta(x - R - 34, y, x - R, y, encurtar=False)
    return s


def seta_reta(x1, y1, x2, y2, encurtar=True):
    if encurtar:
        d = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        x1, y1, x2, y2 = x1 + R * ux, y1 + R * uy, x2 - R * ux, y2 - R * uy
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#333" stroke-width="1.4" marker-end="url(#ponta)"/>')


def rotulo(x, y, texto, ancora="middle", tam=12):
    linhas = texto.split("\n")
    out = ""
    for i, ln in enumerate(linhas):
        out += (f'<text x="{x}" y="{y + i * (tam + 2)}" text-anchor="{ancora}" font-size="{tam}" '
                f'fill="#222">{html.escape(ln)}</text>')
    return out


def laco(x, y, lado, texto):
    if lado == "cima":
        p = f"M {x - 12} {y - 21} C {x - 38} {y - 78}, {x + 38} {y - 78}, {x + 12} {y - 21}"
        lab = rotulo(x, y - 70 - 14 * texto.count("\n"), texto)
    elif lado == "baixo":
        p = f"M {x - 12} {y + 21} C {x - 38} {y + 78}, {x + 38} {y + 78}, {x + 12} {y + 21}"
        lab = rotulo(x, y + 80, texto)
    else:  # direita
        p = f"M {x + 21} {y - 12} C {x + 78} {y - 38}, {x + 78} {y + 38}, {x + 21} {y + 12}"
        lab = rotulo(x + 70, y - 4, texto, "start")
    return f'<path d="{p}" fill="none" stroke="#333" stroke-width="1.4" marker-end="url(#ponta)"/>' + lab


def svg(largura, altura, corpo):
    return (f'<svg viewBox="0 0 {largura} {altura}" width="100%" xmlns="http://www.w3.org/2000/svg">'
            '<defs><marker id="ponta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>'
            f"{corpo}</svg>")


def diagrama_ap():
    xs = [85 + i * 126 for i in range(8)]
    y = 120
    c = ""
    arestas = ["ε, $ / $", "x, $ / x$", "*, y / y", "#, $ / $", "v, $ / K$", "=, K / K", "ε, $ / $"]
    for i, lab in enumerate(arestas):
        c += seta_reta(xs[i], y, xs[i + 1], y) + rotulo((xs[i] + xs[i + 1]) / 2, y - 8, lab)
    c += laco(xs[2], y, "cima", "x, y / xy")
    c += laco(xs[3], y, "cima", "x̄, x / ε")
    c += laco(xs[5], y, "cima", "v, K / KK")
    c += laco(xs[6], y, "cima", "v, K / ε")
    for i, x in enumerate(xs):
        c += estado(x, y, f"q{i}", final=(i == 7), inicial=(i == 0))
    papeis = ["início", "1º mov.", "ida", "volta", "1º vol.", "volumes", "comprov.", "aceita"]
    for x, p in zip(xs, papeis):
        c += rotulo(x, y + 44, p, tam=11)
    return svg(1010, 180, c)


def diagrama_all():
    P = {"q0": (60, 230), "q1": (180, 230), "q2": (420, 100), "q3": (420, 360), "q7": (420, 230),
         "q4": (640, 100), "q5": (640, 360), "q6": (820, 230), "q8": (570, 230), "qA": (700, 230)}
    c = ""

    def e(a, b, lab, dx, dy, ancora="middle"):
        nonlocal c
        (x1, y1), (x2, y2) = P[a], P[b]
        c += seta_reta(x1, y1, x2, y2) + rotulo((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, lab, ancora)

    e("q0", "q1", "< / <, D", 0, -8)
    e("q1", "q2", "p / X, D", -8, -6, "end")
    e("q1", "q3", "g / X, D", -8, 16, "end")
    e("q7", "q2", "p / X, D", 8, 4, "start")
    e("q7", "q3", "g / X, D", 8, 4, "start")
    e("q2", "q4", "= / =, D", 0, -8)
    e("q3", "q5", "= / =, D", 0, -8)
    e("q4", "q6", "p / Y, E", 10, -4, "start")
    e("q5", "q6", "g / Y, E", 10, 12, "start")
    e("q7", "q8", "= / =, D", 0, -8)
    e("q8", "qA", "> / >, P", 0, -8)
    # q6 → q7 (curva por cima de q8 e qA)
    (x6, y6), (x7, y7) = P["q6"], P["q7"]
    c += (f'<path d="M {x6 - 18} {y6 - 16} C {x6 - 110} {y6 - 90}, {x7 + 110} {y7 - 90}, {x7 + 18} {y7 - 16}" '
          f'fill="none" stroke="#333" stroke-width="1.4" marker-end="url(#ponta)"/>')
    c += rotulo((x6 + x7) / 2, y6 - 42, "X / X, D")
    c += laco(*P["q2"], "cima", "p / p, D\ng / g, D")
    c += laco(*P["q3"], "baixo", "p / p, D\ng / g, D")
    c += laco(*P["q4"], "cima", "Y / Y, D")
    c += laco(*P["q5"], "baixo", "Y / Y, D")
    c += laco(*P["q6"], "direita", "p, g, =, Y\n/ (mesmo), E")
    c += laco(*P["q8"], "baixo", "Y / Y, D")
    for nome, (x, y) in P.items():
        c += estado(x, y, nome, final=(nome == "qA"), inicial=(nome == "q0"))
    c += rotulo(10, 20, "qR (rejeição): destino de toda transição ausente", "start", 11)
    return svg(1000, 475, c)


# ------------------------------------------------------------- conteúdo
def capturar(func, *args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(*args)
    return html.escape(buf.getvalue().rstrip())


def derivacao(cadeia):
    passos = gramatica.derivacao_mais_a_esquerda(cadeia)
    larg = max(len(f) for f, _ in passos)
    linhas = []
    for i, (forma, prod) in enumerate(passos):
        linhas.append(f"{'  ' if i == 0 else '⇒ '}{forma:{larg}}   {('[' + prod + ']') if prod else ''}")
    return html.escape("\n".join(linhas))


def tabela_modulo(arquivo, executar):
    dados = json.loads((RAIZ / "tests" / arquivo).read_text(encoding="utf-8"))
    casos = dados["casos"]
    n_ac = sum(c["esperado"] == "aceita" for c in casos)
    out = [f"<h3>Módulo {dados['modulo']}: {n_ac} aceitas, {len(casos) - n_ac} rejeitadas</h3>",
           "<table><tr><th>#</th><th>Entrada</th><th>Tam.</th><th>Esperado</th><th>Obtido</th>"
           "<th>Regra verificada</th><th>Motivo informado pelo autômato</th></tr>"]
    for i, c in enumerate(casos, 1):
        r = executar(c["entrada"])
        ob = "aceita" if r.aceita else "rejeita"
        cls = "ok" if ob == c["esperado"] else "bad"
        ent = f"<code>{html.escape(c['entrada'])}</code>" if c["entrada"] else "<i>(vazia)</i>"
        out.append(f"<tr><td>{i}</td><td>{ent}</td><td class='c'>{len(c['entrada'])}</td><td>{c['esperado']}</td>"
                   f"<td class='{cls}'>{ob}</td><td>{html.escape(c['regra'])}</td>"
                   f"<td>{html.escape(r.motivo)}</td></tr>")
    out.append("</table>")
    return "\n".join(out), len(casos)


def tabela_integracao():
    dados = json.loads((RAIZ / "tests" / "casos_integracao.json").read_text(encoding="utf-8"))
    out = ["<h3>Fluxo completo (integração)</h3>",
           "<table><tr><th>#</th><th>Entrada</th><th>Tam.</th><th>Esperado AP</th><th>Obtido AP</th>"
           "<th>Esperado ALL</th><th>Obtido ALL</th><th>Regra verificada</th></tr>"]
    for i, c in enumerate(dados["casos"], 1):
        f = executar_fluxo(c["entrada"])
        ap = "aceita" if f.ap.aceita else "rejeita"
        al = "não executado" if f.all is None else ("aceita" if f.all.aceita else "rejeita")
        out.append(f"<tr><td>{i}</td><td><code>{c['entrada']}</code></td><td class='c'>{len(c['entrada'])}</td>"
                   f"<td>{c['esperado_ap']}</td><td>{ap}</td><td>{c['esperado_all'].replace('nao_executado', 'não executado')}</td>"
                   f"<td>{al}</td><td>{html.escape(c['regra'])}</td></tr>")
    out.append("</table><h3>Símbolo fora do alfabeto de entrada</h3>")
    for c in dados["simbolo_invalido"]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            codigo = cli_main(["-m", c["modulo"], c["entrada"]])
        out.append(f"<p>Comando <code>py -m validador -m {c['modulo']} \"{c['entrada']}\"</code> "
                   f"(código de saída {codigo}). Mensagem exibida:</p><pre>{html.escape(buf.getvalue().strip())}</pre>")
    return "\n".join(out)


def gerar_pdf(html_path: Path, pdf_path: Path) -> bool:
    candidatos = [
        shutil.which("msedge"), shutil.which("chrome"), shutil.which("google-chrome"), shutil.which("chromium"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for exe in candidatos:
        if exe and Path(exe).exists():
            subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                           check=False, capture_output=True, timeout=120)
            return pdf_path.exists()
    return False


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    c1 = "NNLLN*SOOSS#ppgp=ppgp"
    t_ap, n_ap = tabela_modulo("casos_ap.json", executar_ap)
    t_all, n_all = tabela_modulo("casos_all.json", executar_all)
    u200 = "pg" * 100
    subs = {
        "DERIVACAO": derivacao(c1),
        "TRACE_AP": capturar(imprimir_rastro_ap, executar_ap(c1)),
        "TRACE_ALL": capturar(imprimir_rastro_all, executar_all("ppgp=pgpp")),
        "TRACE_ALL_CURTO": capturar(imprimir_rastro_all, executar_all("pg=pg")),
        "DIAGRAMA_AP": diagrama_ap(),
        "DIAGRAMA_ALL": diagrama_all(),
        "TESTES": t_ap + "\n" + t_all + "\n" + tabela_integracao(),
        "N_AP": str(n_ap),
        "N_ALL": str(n_all),
        "PASSOS_C1": str(len(executar_all("ppgp=ppgp").rastro) - 1),
        "PASSOS_200": f"{len(executar_all(u200 + '=' + u200).rastro) - 1:,}".replace(",", "."),
    }
    texto = (DOCS / "relatorio_modelo.html").read_text(encoding="utf-8")
    for k, v in subs.items():
        texto = texto.replace("{{" + k + "}}", v)
    assert "{{" not in texto, "placeholder não substituído"
    saida = DOCS / "relatorio.html"
    saida.write_text(texto, encoding="utf-8")
    print(f"Gerado {saida}")
    pdf = DOCS / "relatorio.pdf"
    if gerar_pdf(saida, pdf):
        print(f"Gerado {pdf}")
    else:
        print("PDF não gerado (Edge/Chrome não encontrado): abra o HTML no navegador e use Imprimir → Salvar como PDF.")


if __name__ == "__main__":
    main()
