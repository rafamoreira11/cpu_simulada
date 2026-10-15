# CPU Simulada de 8 bits

Trabalho prático de Arquitetura de Computadores – UFC Sobral (2026.2).
Implementação em Python de uma CPU didática com ULA, registradores, memória,
conjunto reduzido de instruções e ciclo **Fetch → Decode → Execute**.

**Autor(es):** _(preencher com os nomes da dupla)_

## Arquitetura

| Componente          | Especificação                              |
|---------------------|--------------------------------------------|
| Tamanho dos dados   | 8 bits (0 a 255)                           |
| Registradores       | R0, R1, R2, R3                             |
| Contador de programa| PC                                         |
| Memória             | 16 posições (endereços 0 a 15)             |
| ULA                 | ADD, SUB, AND, OR, XOR                     |
| Execução            | Fetch → Decode → Execute                   |

```
 Memória (16x8) <--endereço/dados--> [ Registradores R0..R3 + PC ] <--> ULA
                                              ^
                                     Unidade de Controle
                                     (fetch/decode/execute)
```

### Decisões de projeto

- **Representação da memória:** cada posição guarda ou uma *string* com a
  instrução (ex.: `"ADD R0, R1"`) ou um número inteiro (dado). Instruções e
  dados dividem os mesmos 16 endereços.
- **Limite de 8 bits:** todo resultado da ULA e todo `LOAD` passam por
  `valor & 0xFF`. Assim `200 + 100 = 44` (estouro) e `3 - 5 = 254`
  (complemento de dois).
- **HALT:** marca `halted = True` e o PC permanece no HALT.
- **Erros tratados:** instrução desconhecida, número errado de operandos,
  registrador inexistente, endereço fora de 0–15, PC apontando para um dado
  (programa sem HALT) e laço infinito (limite de ciclos).
- A vírgula entre operandos é opcional e as instruções não diferenciam
  maiúsculas de minúsculas.

## Conjunto de instruções

| Instrução      | Função                                  |
|----------------|-----------------------------------------|
| `LOAD Rx, n`   | Rx ← n (8 bits)                         |
| `STORE Rx, a`  | MEM[a] ← Rx                             |
| `ADD Rx, Ry`   | Rx ← Rx + Ry                            |
| `SUB Rx, Ry`   | Rx ← Rx − Ry                            |
| `AND Rx, Ry`   | Rx ← Rx AND Ry                          |
| `OR Rx, Ry`    | Rx ← Rx OR Ry                           |
| `XOR Rx, Ry`   | Rx ← Rx XOR Ry                          |
| `JMP a`        | PC ← a                                  |
| `HALT`         | Encerra a execução                      |

## Arquivos

| Arquivo        | Conteúdo                                              |
|----------------|-------------------------------------------------------|
| `ula.py`       | ULA e função `limitar_8bits`                          |
| `cpu.py`       | Classe `CPU`: `fetch`, `decode`, `execute`, `ciclo`   |
| `programas.py` | Programas: `exemplo`, `proprio`, `overflow`           |
| `testes.py`    | 40 testes automáticos (`unittest`)                    |
| `main.py`      | Execução e visualização passo a passo                 |

## Como executar

Requer Python 3.8+ (sem dependências externas).

```bash
python main.py                         # programa do enunciado (5 + 8)
python main.py --passo                 # passo a passo (ENTER a cada ciclo)
python main.py --programa proprio      # programa próprio do grupo
python main.py --programa overflow     # demonstra o limite de 8 bits
python testes.py                       # roda todos os testes
```

A cada ciclo são exibidos o PC, a instrução, os registradores (em
hexadecimal) e, após a execução, o novo PC e os registradores em hexadecimal
e decimal:

```
-----------------------------
PC: 02
Instrução: ADD R0, R1
R0 = 05 R1 = 08 R2 = 00 R3 = 00
Executando...
Depois -> PC: 03  R0 = 0D (13) R1 = 08 (8) R2 = 00 (0) R3 = 00 (0)
```

## Programa de exemplo (enunciado)

```
LOAD R0, 5
LOAD R1, 8
ADD R0, R1
STORE R0, 15
HALT
```
Resultado: `MEM[15] = 13`.

## Programa próprio (12 instruções)

Usa LOAD, STORE, AND, OR, XOR, SUB e JMP:

```
00 LOAD R0, 12    ; R0 = 12 (1100)
01 LOAD R1, 10    ; R1 = 10 (1010)
02 AND R0, R1     ; R0 = 8  (1000)
03 LOAD R2, 12    ; R2 = 12
04 OR R2, R1      ; R2 = 14 (1110)
05 XOR R2, R0     ; R2 = 6  (0110)
06 JMP 8          ; PC = 8 (pula o endereço 7)
07 LOAD R3, 99    ; nunca executada
08 SUB R0, R2     ; R0 = 8 - 6 = 2
09 STORE R2, 14   ; MEM[14] = 6
10 STORE R0, 15   ; MEM[15] = 2
11 HALT
```

Evolução do PC: 0 → 1 → 2 → 3 → 4 → 5 → 6 → **8** → 9 → 10 → 11 (11 ciclos).
Resultado final: `MEM[14] = 6`, `MEM[15] = 2`, `R3 = 0`.

## Testes

`python testes.py` cobre: cada operação da ULA, estouro e subtração negativa
em 8 bits, LOAD, STORE, avanço do PC, JMP, HALT, os programas completos
(incluindo o exemplo, com `MEM[15] = 13`) e as situações de erro.
