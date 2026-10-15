"""
programas.py - Programas usados nos testes e na demonstração.
Cada programa é uma lista de instruções; o índice é o endereço na memória.
"""

# Programa do enunciado: 5 + 8, resultado em MEM[15] (esperado: 13)
PROGRAMA_EXEMPLO = [
    "LOAD R0, 5",
    "LOAD R1, 8",
    "ADD R0, R1",
    "STORE R0, 15",
    "HALT",
]

# Programa próprio (12 instruções): usa LOAD, STORE, AND, OR, XOR, SUB e JMP.
#   R0 = 12 AND 10 = 8
#   R2 = (12 OR 10) XOR 8 = 14 XOR 8 = 6
#   JMP 8 pula a instrução do endereço 7 (R3 continua 0)
#   R0 = 8 - 6 = 2
# Resultado esperado: MEM[14] = 6 e MEM[15] = 2
PROGRAMA_PROPRIO = [
    "LOAD R0, 12",    # 00: R0 = 12 (1100)
    "LOAD R1, 10",    # 01: R1 = 10 (1010)
    "AND R0, R1",     # 02: R0 = 8  (1000)
    "LOAD R2, 12",    # 03: R2 = 12
    "OR R2, R1",      # 04: R2 = 14 (1110)
    "XOR R2, R0",     # 05: R2 = 6  (0110)
    "JMP 8",          # 06: salta para o endereço 8
    "LOAD R3, 99",    # 07: nunca executada
    "SUB R0, R2",     # 08: R0 = 8 - 6 = 2
    "STORE R2, 14",   # 09: MEM[14] = 6
    "STORE R0, 15",   # 10: MEM[15] = 2
    "HALT",           # 11
]

# Demonstra o limite de 8 bits: 200 + 100 = 300 -> 44 e 3 - 5 -> 254
PROGRAMA_OVERFLOW = [
    "LOAD R0, 200",
    "LOAD R1, 100",
    "ADD R0, R1",     # R0 = 44
    "LOAD R2, 3",
    "LOAD R3, 5",
    "SUB R2, R3",     # R2 = 254
    "STORE R0, 14",
    "STORE R2, 15",
    "HALT",
]

PROGRAMAS = {
    "exemplo": PROGRAMA_EXEMPLO,
    "proprio": PROGRAMA_PROPRIO,
    "overflow": PROGRAMA_OVERFLOW,
}
