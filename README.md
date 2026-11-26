# Validador de missões de drone: AP + ALL

Trabalho prático de **Linguagens Formais e Autômatos**: reconhecimento de linguagens com pilha e fita limitada.

O programa valida o registro de uma missão de drone de entrega em duas etapas:

| Etapa | Autômato | O que verifica | Classe da regra |
|---|---|---|---|
| 1 | **Autômato de pilha (AP)** | A volta desfaz a ida, e há tantos comprovantes quanto volumes | livre de contexto |
| 2 | **Autômato linearmente limitado (ALL)** | Os comprovantes repetem os volumes, na mesma ordem | sensível ao contexto |

O ALL só roda se o AP aceitar, e recebe apenas o trecho depois do `#`.

## Formato da entrada

Exemplo: `NNLLN*SOOSS#ppgp=ppgp`

| Trecho | `NNLLN` | `*` | `SOOSS` | `#` | `ppgp` | `=` | `ppgp` |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Significado | ida | ponto de entrega | volta | fim da rota | volumes embarcados | separador | comprovantes de entrega |

- **Movimentos:** `N`, `S`, `L`, `O` (Norte, Sul, Leste, Oeste). A volta é a ida de trás para frente, com direções opostas (N↔S, L↔O): ida `NNLLN` exige volta `SOOSS`.
- **Volumes e comprovantes:** `p` (pequeno) e `g` (grande). O i-ésimo comprovante corresponde ao i-ésimo volume.

### Linguagens

Linguagem do AP: livre de contexto, mas não regular.

```
L_AP = { w * inv(w)^R # u = v  :  w ∈ {N,S,L,O}+,  u,v ∈ {p,g}+,  |u| = |v| }
```

Linguagem do ALL: sensível ao contexto, mas não livre de contexto.

```
L_ALL = { u = u  :  u ∈ {p,g}+ }
```

`inv` troca N↔S e L↔O.

### Documentos

| Documento | Conteúdo |
|---|---|
| [docs/relatorio.pdf](docs/relatorio.pdf) | Relatório técnico: GLC, especificações dos autômatos, provas de classificação e análise dos testes (também em [HTML](docs/relatorio.html)) |
| [docs/slides.pdf](docs/slides.pdf) | Slides da apresentação (18 slides) |

### Os três cenários de integração

| Entrada | AP | ALL | Motivo |
|---|---|---|---|
| `NNLLN*SOOSS#ppgp=ppgp` | ✅ aceita | ✅ aceita | tudo confere |
| `NNLLN*SOSOS#ppgp=ppgp` | ❌ rejeita | não executa | a volta não desfaz a ida |
| `NNLLN*SOOSS#ppgp=pgpp` | ✅ aceita | ❌ rejeita | 4 comprovantes para 4 volumes, mas fora de ordem |

## Instalação

Requer **Python 3.10 ou superior** (testado com 3.14 no Windows 11). Não há dependências externas: o programa usa só a biblioteca padrão, e o [requirements.txt](requirements.txt) está vazio de propósito.

```bash
git clone https://github.com/murilpcarneiro/validador-missoes-drone.git
cd validador-missoes-drone
```

No Windows use `py`; no Linux e no macOS troque por `python3` nos comandos abaixo.

## Como executar

| Comando | O que faz |
|---|---|
| `py -m validador "NNLLN*SOOSS#ppgp=ppgp"` | fluxo completo (AP → ALL) |
| `py -m validador -t "NNLLN*SOOSS#ppgp=ppgp"` | fluxo completo com rastreamento |
| `py -m validador -m ap -t "N*S#p=p"` | só o AP, com rastreamento |
| `py -m validador -m all -t "pgp=pgp"` | só o ALL, com rastreamento |
| `py -m validador -d "NNLLN*SOOSS#ppgp=ppgp"` | derivação mais à esquerda na GLC |
| `py -m validador --demo` | os 3 cenários de integração e uma derivação |
| `py -m validador --spec` | imprime a GLC e todas as transições do AP e do ALL |
| `py -m validador -a exemplos/entradas.txt` | valida cada linha de um arquivo |
| `py -m validador` | modo interativo (prefixos `ap:`, `all:`, `der:`; sufixo `-t` para rastreamento) |

**Rastreamentos.** No AP, cada linha mostra o estado, a posição de leitura (com o símbolo lido em destaque), a pilha com o topo à esquerda e a transição aplicada. No ALL, mostra o estado, a posição do cabeçote, a fita inteira entre os marcadores `<` e `>` (com a célula sob o cabeçote em destaque) e a transição. No ALL, uma linha horizontal separa cada rodada de conferência.

A saída usa cores e tabelas com bordas no terminal. As cores se desligam sozinhas quando a saída vai para um arquivo ou quando a variável `NO_COLOR` está definida; `--sem-cor` também as desliga. Sem cores, o destaque aparece como `[x]`.

## Testes

```bash
py tests/executar_testes.py                # testes obrigatórios; grava tests/RESULTADOS.md
py -m unittest discover -s tests -v        # suíte completa, com os testes exaustivos (~20 s)
```

| Arquivo | Conteúdo |
|---|---|
| [tests/casos_ap.json](tests/casos_ap.json) | 9 aceitas e 12 rejeitadas pelo AP, incluindo os casos-limite `N*S#p=p` e a entrada vazia |
| [tests/casos_all.json](tests/casos_all.json) | 9 aceitas e 11 rejeitadas pelo ALL, incluindo os casos-limite `p=p`, a entrada vazia e `=` |
| [tests/casos_integracao.json](tests/casos_integracao.json) | os 3 cenários de integração e as entradas com símbolo fora do alfabeto |
| [tests/RESULTADOS.md](tests/RESULTADOS.md) | registro de cada teste: entrada, decisão esperada, decisão obtida, regra verificada e motivo dado pelo autômato |

A suíte `unittest` também compara o AP, a GLC e a definição matemática de L_AP em **todas** as 2.396.745 cadeias de até 7 símbolos sobre um sub-alfabeto. Também compara o ALL com a definição de L_ALL em todas as 88.573 cadeias de até 10 símbolos sobre {p, g, =}.

Para gerar de novo o relatório (HTML e PDF, via Edge ou Chrome em modo headless) com rastreamentos e tabelas atualizados:

```bash
py docs/gerar_relatorio.py
```

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `validador/ap.py` | simulador genérico de AP determinístico e o AP do projeto (8 estados) |
| `validador/lba.py` | simulador genérico de ALL determinístico e o ALL do projeto (11 estados, fita de n + 2 células) |
| `validador/gramatica.py` | GLC, árvore sintática e derivação mais à esquerda |
| `validador/pipeline.py` | verificação do alfabeto e fluxo AP → ALL |
| `validador/estilo.py` | cores e tabelas do terminal |
| `validador/__main__.py` | interface de linha de comando |
| `tests/` | casos em JSON, executor dos testes obrigatórios e suíte `unittest` |
| `exemplos/` | entradas de exemplo, saída da demonstração e especificação impressa |
| `docs/` | relatório técnico (HTML e PDF), o script que o gera e os slides da apresentação |

## Equipe

| Nome completo | Parte técnica na apresentação |
|---|---|
| Murilo Pantoja Carneiro | Problema, GLC, derivação e prova de não regularidade; limitações |
| Vithor dos Santos Santa Rosa | Autômato de pilha: diagrama, rastreamento, relação GLC ↔ AP e terminação |
| João Felipe da Rocha Soares | Linguagem sensível ao contexto, ALL e fita limitada; testes |

## Origem do código e uso de inteligência artificial

O código, os casos de teste, os diagramas e o relatório foram produzidos para este trabalho; não foram adaptados de exercícios de sala nem do exemplo da lauda. Os conceitos seguem as referências citadas no relatório (Sipser; Hopcroft, Motwani e Ullman; Menezes).

**Uso de IA:** a equipe usou o **Claude (Anthropic), via Claude Code**, como apoio para propor o problema e as linguagens, escrever o código dos simuladores, gerar os casos de teste e a suíte `unittest`, e redigir o rascunho do relatório e deste README.

**O que a equipe verificou:**

- executamos os testes obrigatórios e a suíte `unittest` e conferimos que tudo passa;
- simulamos à mão os três cenários de integração e comparamos com o rastreamento do programa;
- comparamos as tabelas de transição do relatório com o código (`--spec`) e com os diagramas;
- refizemos as provas pelo lema do bombeamento e revisamos o texto do relatório.
