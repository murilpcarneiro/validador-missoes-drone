# Resultados dos testes obrigatórios

Gerado automaticamente por `py tests/executar_testes.py`.
Cadeias regulares de teste têm no mínimo 18 símbolos; as marcadas como CASO-LIMITE são exceções propositais.

## Módulo AP (9 aceitas, 12 rejeitadas)

| # | Entrada | Tam. | Esperado | Obtido | OK | Regra verificada | Motivo informado pelo autômato |
|---|---|---|---|---|---|---|---|
| 1 | `NNLLN*SOOSS#ppgp=ppgp` | 21 | aceita | aceita | ✅ | volta = ida invertida; 4 volumes e 4 comprovantes | entrada consumida e q7 é estado final |
| 2 | `NNLLN*SOOSS#ppgp=pgpp` | 21 | aceita | aceita | ✅ | AP só confere quantidade (4 = 4), não a ordem | entrada consumida e q7 é estado final |
| 3 | `LLNNO*LSSOO#gggp=pggg` | 21 | aceita | aceita | ✅ | volta = ida invertida; 4 = 4 | entrada consumida e q7 é estado final |
| 4 | `SSSOL*OLNNN#pgpg=gpgp` | 21 | aceita | aceita | ✅ | volta = ida invertida; 4 = 4 | entrada consumida e q7 é estado final |
| 5 | `NLSO*LNOS#ppppp=ggggg` | 21 | aceita | aceita | ✅ | AP só confere quantidade (5 = 5) | entrada consumida e q7 é estado final |
| 6 | `OOOOOO*LLLLLL#pg=gp` | 19 | aceita | aceita | ✅ | 6 movimentos O desfeitos por 6 L; 2 = 2 | entrada consumida e q7 é estado final |
| 7 | `NLNLNLNL*OSOSOSOS#g=g` | 21 | aceita | aceita | ✅ | ida longa (8) com volta invertida; 1 = 1 | entrada consumida e q7 é estado final |
| 8 | `SLNOSL*ONLSON#pgg=pgg` | 21 | aceita | aceita | ✅ | volta = ida invertida; 3 = 3 | entrada consumida e q7 é estado final |
| 9 | `N*S#p=p` | 7 | aceita | aceita | ✅ | CASO-LIMITE: menor cadeia aceita (\|w\| = \|u\| = \|v\| = 1) | entrada consumida e q7 é estado final |
| 10 | `NNLLN*SOSOS#ppgp=ppgp` | 21 | rejeita | rejeita | ✅ | volta fora de ordem (3º movimento S, topo L) | sem transição para (q3, 'S', topo L) na posição 8: a volta deve repetir a ida ao contrário com direções inversas, seguida de '#' |
| 11 | `NNLLN*SOOS#ppgp=ppgp` | 20 | rejeita | rejeita | ✅ | volta mais curta que a ida | sem transição para (q3, '#', topo N) na posição 10: a volta é mais curta que a ida (ainda há movimentos na pilha) |
| 12 | `NNLLN*SOOSSS#ppgp=ppgp` | 22 | rejeita | rejeita | ✅ | volta mais longa que a ida | sem transição para (q3, 'S', topo $) na posição 11: a volta deve repetir a ida ao contrário com direções inversas, seguida de '#' |
| 13 | `NNLLN*SOOSS#ppgp=ppg` | 20 | rejeita | rejeita | ✅ | menos comprovantes que volumes | entrada consumida, mas q6 não é estado final: há menos comprovantes do que volumes embarcados |
| 14 | `NNLLN*SOOSS#ppgp=ppgpg` | 22 | rejeita | rejeita | ✅ | mais comprovantes que volumes | sem transição para (q7, 'g', topo $) na posição 21: todos os volumes já foram comprovados, mas ainda há símbolos (comprovantes a mais ou símbolos excedentes) |
| 15 | `NNLLNSOOSS#ppgp=ppgp` | 20 | rejeita | rejeita | ✅ | falta o ponto de entrega '*' | sem transição para (q2, '#', topo S) na posição 10: esperado movimento da ida ou '*' (ponto de entrega) |
| 16 | `NNLLN*SOOSS#=ppgpppgp` | 21 | rejeita | rejeita | ✅ | nenhum volume embarcado antes de '=' | sem transição para (q4, '=', topo $) na posição 12: o manifesto deve começar com um volume p ou g |
| 17 | `NNLLN*SOOSSppgp=ppgp` | 20 | rejeita | rejeita | ✅ | falta o separador '#' | sem transição para (q3, 'p', topo $) na posição 11: a volta deve repetir a ida ao contrário com direções inversas, seguida de '#' |
| 18 | `*NNLLNSOOSS#ppgp=ppgp` | 21 | rejeita | rejeita | ✅ | rota de ida vazia | sem transição para (q1, '*', topo $) na posição 0: a rota de ida deve começar com um movimento N, S, L ou O |
| 19 | `NNLLN*SOOSS#pp=gp=ppgp` | 22 | rejeita | rejeita | ✅ | dois separadores '=' | sem transição para (q7, '=', topo $) na posição 17: todos os volumes já foram comprovados, mas ainda há símbolos (comprovantes a mais ou símbolos excedentes) |
| 20 | `NNLLN*SOOSS#ppgp=ppgp#` | 22 | rejeita | rejeita | ✅ | símbolo excedente após o manifesto | sem transição para (q7, '#', topo $) na posição 21: todos os volumes já foram comprovados, mas ainda há símbolos (comprovantes a mais ou símbolos excedentes) |
| 21 | *(vazia)* | 0 | rejeita | rejeita | ✅ | CASO-LIMITE: entrada vazia | entrada consumida, mas q1 não é estado final: a rota de ida deve começar com um movimento N, S, L ou O |

## Módulo ALL (9 aceitas, 11 rejeitadas)

| # | Entrada | Tam. | Esperado | Obtido | OK | Regra verificada | Motivo informado pelo autômato |
|---|---|---|---|---|---|---|---|
| 1 | `ppgpgggpp=ppgpgggpp` | 19 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 2 | `ggggggggg=ggggggggg` | 19 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 3 | `ppppppppp=ppppppppp` | 19 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 4 | `pgpgpgpgp=pgpgpgpgp` | 19 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 5 | `gpgpgpgpgp=gpgpgpgpgp` | 21 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 6 | `pppppgggggp=pppppgggggp` | 23 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 7 | `gppggppggp=gppggppggp` | 21 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 8 | `pggpgppgpg=pggpgppgpg` | 21 | aceita | aceita | ✅ | comprovantes = volumes, mesma ordem | alcançou qA: comprovantes conferem com o embarque |
| 9 | `p=p` | 3 | aceita | aceita | ✅ | CASO-LIMITE: menor cadeia aceita (\|u\| = 1) | alcançou qA: comprovantes conferem com o embarque |
| 10 | `ppgpgggpp=ppgpggpgp` | 19 | rejeita | rejeita | ✅ | mesmo tamanho, 7º comprovante difere | sem transição para (q5, 'p') na célula 17 → qR: comprovante 'p' onde o embarque exigia 'g' (ordem/tipo diferente) |
| 11 | `ppgpgggpp=ppgpgggp` | 18 | rejeita | rejeita | ✅ | um comprovante a menos | sem transição para (q4, '>') na célula 19 → qR: há menos comprovantes do que volumes |
| 12 | `ppgpgggpp=ppgpgggppg` | 20 | rejeita | rejeita | ✅ | um comprovante a mais | sem transição para (q8, 'g') na célula 20 → qR: há mais comprovantes do que volumes |
| 13 | `ggggggggg=ppppppppp` | 19 | rejeita | rejeita | ✅ | tipos trocados em todas as posições | sem transição para (q5, 'p') na célula 11 → qR: comprovante 'p' onde o embarque exigia 'g' (ordem/tipo diferente) |
| 14 | `pgpgpgpgp=gpgpgpgpg` | 19 | rejeita | rejeita | ✅ | comprovantes deslocados de uma posição | sem transição para (q4, 'g') na célula 11 → qR: comprovante 'g' onde o embarque exigia 'p' (ordem/tipo diferente) |
| 15 | `pppppggggg=gggggppppp` | 21 | rejeita | rejeita | ✅ | comprovantes na ordem inversa (w = w^R não basta) | sem transição para (q4, 'g') na célula 12 → qR: comprovante 'g' onde o embarque exigia 'p' (ordem/tipo diferente) |
| 16 | `pgpgpgpgppgpgpgpgp` | 18 | rejeita | rejeita | ✅ | sem separador '=' | sem transição para (q2, '>') na célula 19 → qR: falta o separador '=' |
| 17 | `ppgpg=ggpp=ppgpgggpp` | 20 | rejeita | rejeita | ✅ | dois separadores '=' | sem transição para (q4, 'g') na célula 7 → qR: comprovante 'g' onde o embarque exigia 'p' (ordem/tipo diferente) |
| 18 | `=ppgpgggppppgpgggpp` | 19 | rejeita | rejeita | ✅ | nenhum volume antes de '=' | sem transição para (q1, '=') na célula 1 → qR: não há volumes embarcados antes do '=' |
| 19 | *(vazia)* | 0 | rejeita | rejeita | ✅ | CASO-LIMITE: entrada vazia | sem transição para (q1, '>') na célula 1 → qR: entrada vazia |
| 20 | `=` | 1 | rejeita | rejeita | ✅ | CASO-LIMITE: só o separador (u vazio) | sem transição para (q1, '=') na célula 1 → qR: não há volumes embarcados antes do '=' |

## Fluxo completo (integração AP → ALL)

| # | Entrada | Tam. | Esperado AP | Obtido AP | Esperado ALL | Obtido ALL | OK | Regra verificada |
|---|---|---|---|---|---|---|---|---|
| 1 | `NNLLN*SOOSS#ppgp=ppgp` | 21 | aceita | aceita | aceita | aceita | ✅ | estrutura válida e comprovantes na mesma ordem do embarque |
| 2 | `NNLLN*SOSOS#ppgp=ppgp` | 21 | rejeita | rejeita | nao_executado | nao_executado | ✅ | a volta não desfaz a ida (regra livre de contexto) |
| 3 | `NNLLN*SOOSS#ppgp=pgpp` | 21 | aceita | aceita | rejeita | rejeita | ✅ | 4 = 4 comprovantes, mas fora da ordem (regra sensível ao contexto) |

## Símbolo fora do alfabeto de entrada

Comando: `py -m validador -m fluxo "NNLLX*SOOSS#ppgp=ppgp"` (código de saída 2)

```
ERRO (AP): símbolo 'X' na posição 4 não pertence ao alfabeto de entrada Σ = {#, *, =, L, N, O, S, g, p}. Nenhum autômato foi executado.
```

Comando: `py -m validador -m all "ppgpgggpp=ppgpgggpx"` (código de saída 2)

```
ERRO (ALL): símbolo 'x' na posição 18 não pertence ao alfabeto de entrada Σ = {=, g, p}. Nenhum autômato foi executado.
```


## Resumo

Todos os testes passaram.
