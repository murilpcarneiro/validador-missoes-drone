# Validador de missões de drone: AP + ALL

Trabalho prático de Linguagens Formais e Autômatos: reconhecimento de linguagens com pilha e fita limitada.

A aplicação valida o **registro de uma missão de drone de entrega** em duas etapas:

1. **Autômato de pilha (AP)** verifica a estrutura livre de contexto: a rota de volta desfaz a ida (mesmo corredor aéreo, ordem inversa, direções opostas) e o manifesto tem tantos comprovantes quanto volumes embarcados.
2. **Autômato linearmente limitado (ALL)** recebe o trecho após `#` e verifica a regra sensível ao contexto: os comprovantes de entrega repetem **exatamente** a sequência de volumes embarcados, na mesma ordem.

```
NNLLN*SOOSS#ppgp=ppgp
└─ida─┘└volta┘ └u─┘ └v─┘
     ponto de    volumes  comprovantes
     entrega *   embarcados
```

| Símbolo | Significado |
|---|---|
| `N S L O` | movimento para Norte, Sul, Leste, Oeste |
| `*` | ponto de entrega (início da volta) |
| `#` | fim da rota / início do manifesto de carga |
| `p g` | volume pequeno / grande |
| `=` | separa volumes embarcados de comprovantes de entrega |

| Linguagem | Definição | Classe |
|---|---|---|
| L_AP | `{ w * inv(w)^R # u = v : w ∈ {N,S,L,O}+, u,v ∈ {p,g}+, \|u\| = \|v\| }` | livre de contexto, não regular |
| L_ALL | `{ u = u : u ∈ {p,g}+ }` | sensível ao contexto, não livre de contexto |

`inv` troca N↔S e L↔O. A especificação formal completa, as provas de classificação e a análise dos testes estão em [docs/relatorio.html](docs/relatorio.html) (e na versão PDF [docs/relatorio.pdf](docs/relatorio.pdf)).

## Requisitos

- Python **3.10 ou superior** (testado com 3.14 no Windows 11).
- Nenhuma dependência externa: só a biblioteca padrão ([requirements.txt](requirements.txt) está vazio de propósito).

## Instalação

```bash
git clone https://github.com/murilpcarneiro/validador-missoes-drone.git
cd validador-missoes-drone
```

No Windows use `py`; no Linux/macOS use `python3` nos comandos abaixo.

## Execução

```bash
py -m validador "NNLLN*SOOSS#ppgp=ppgp"          # fluxo completo (AP → ALL)
py -m validador -t "NNLLN*SOOSS#ppgp=ppgp"       # fluxo completo com rastreamento
py -m validador -m ap -t "N*S#p=p"               # só o AP, com rastreamento
py -m validador -m all -t "pgp=pgp"              # só o ALL, com rastreamento
py -m validador -d "NNLLN*SOOSS#ppgp=ppgp"       # derivação mais à esquerda na GLC
py -m validador --demo                           # os 3 cenários de integração + derivação
py -m validador --spec                           # imprime GLC, AP e ALL (todas as transições)
py -m validador -a exemplos/entradas.txt         # valida cada linha de um arquivo
py -m validador                                  # modo interativo
```

A saída usa cores e tabelas com bordas quando roda num terminal. Use `--sem-cor` para desligar as cores (elas também saem automaticamente quando a saída é redirecionada para um arquivo ou quando a variável `NO_COLOR` está definida).

No modo interativo, use os prefixos `ap:`, `all:` ou `der:` e o sufixo ` -t` para rastreamento.

**Rastreamento do AP:** passo, estado, posição de leitura, entrada restante, conteúdo da pilha (topo à esquerda) e transição aplicada.
**Rastreamento do ALL:** passo, estado, posição do cabeçote e fita completa (`<` e `>` são os marcadores de borda; `[x]` marca a célula sob o cabeçote).

## Testes

```bash
py tests/executar_testes.py                      # testes obrigatórios → gera tests/RESULTADOS.md
py -m unittest discover -s tests -v              # suíte completa (inclui testes exaustivos, ~20 s)
```

- [tests/casos_ap.json](tests/casos_ap.json): 9 aceitas e 12 rejeitadas para o AP (inclui os casos-limite `N*S#p=p` e entrada vazia).
- [tests/casos_all.json](tests/casos_all.json): 9 aceitas e 11 rejeitadas para o ALL (inclui os casos-limite `p=p`, vazia e `=`).
- [tests/casos_integracao.json](tests/casos_integracao.json): os 3 cenários do fluxo completo e as entradas com símbolo fora do alfabeto.
- [tests/RESULTADOS.md](tests/RESULTADOS.md): registro gerado com entrada, decisão esperada, decisão obtida, regra verificada e motivo dado pelo autômato.

Para regenerar o relatório (HTML + PDF via Edge/Chrome headless) com rastreamentos e tabelas atualizados: `py docs/gerar_relatorio.py`.

A suíte `unittest` também compara **AP, GLC e a definição matemática** de L_AP em todas as cadeias de até 7 símbolos sobre um sub-alfabeto, e **ALL com a definição** de L_ALL em todas as cadeias de até 10 símbolos sobre {p, g, =}.

## Estrutura

```
validador/
  ap.py          AP determinístico genérico + AP do projeto (8 estados)
  lba.py         ALL determinístico genérico + ALL do projeto (11 estados), fita de n+2 células
  gramatica.py   GLC, árvore sintática e derivação mais à esquerda
  pipeline.py    verificação do alfabeto e fluxo AP → ALL
  __main__.py    interface de linha de comando
tests/           casos em JSON, executor dos testes obrigatórios, suíte unittest
exemplos/        entradas de exemplo, saída da demonstração e especificação impressa
docs/            relatório técnico (HTML e PDF)
```

## Exemplos de saída

```
>>> RESULTADO FINAL: ACEITA (AP e ALL)                          NNLLN*SOOSS#ppgp=ppgp
>>> RESULTADO FINAL: REJEITADA pelo AP (ALL não executado)      NNLLN*SOSOS#ppgp=ppgp
>>> RESULTADO FINAL: aceita pelo AP, REJEITADA pelo ALL         NNLLN*SOOSS#ppgp=pgpp
ERRO (AP): símbolo 'X' na posição 4 não pertence ao alfabeto de entrada Σ = {#, *, =, L, N, O, S, g, p}. Nenhum autômato foi executado.
```

A saída completa com rastreamentos está em [exemplos/demo_saida.txt](exemplos/demo_saida.txt).

## Origem do código e uso de inteligência artificial

O código, os casos de teste, os diagramas e o relatório foram produzidos para este trabalho; não foram adaptados de exercícios de sala nem do exemplo da lauda. Os conceitos seguem as referências citadas no relatório (Sipser; Hopcroft, Motwani e Ullman; Menezes).

**Uso de IA:** a equipe usou o **Claude (Anthropic), via Claude Code**, como apoio para: propor o problema e as linguagens, escrever o código dos simuladores, gerar os casos de teste e a suíte `unittest`, e redigir o rascunho do relatório e deste README.
**O que a equipe verificou:** *(preencher pela equipe)*. Por exemplo: refazer à mão as provas pelo lema do bombeamento, simular no papel os rastreamentos dos três cenários, conferir cada transição das tabelas com o código e rodar os testes.

## Equipe

| Nome completo | Parte técnica na apresentação |
|---|---|
| Murilo Pantoja Carneiro | Problema, GLC, derivação e prova de não regularidade; limitações |
| Vithor dos Santos Santa Rosa | Autômato de pilha: diagrama, rastreamento, relação GLC ↔ AP e terminação |
| João Felipe da Rocha Soares | Linguagem sensível ao contexto, ALL e fita limitada; testes |
