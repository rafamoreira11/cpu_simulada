"""
ula.py - Unidade Lógica e Aritmética (ULA) de 8 bits.

A ULA recebe dois operandos de 8 bits e uma operação, e devolve
sempre um resultado limitado a 8 bits (0 a 255).
"""

OPERACOES_ULA = ("ADD", "SUB", "AND", "OR", "XOR")


def limitar_8bits(valor):
    """Garante que o valor caiba em 8 bits (descarta o 'vai-um' / empréstimo).

    Exemplos:
        200 + 100 = 300 -> 300 & 0xFF = 44
        3 - 5 = -2      -> -2 & 0xFF  = 254 (complemento de dois)
    """
    return valor & 0xFF


def ula(operacao, a, b):
    """Executa a operação da ULA sobre a e b e devolve o resultado (8 bits)."""
    if operacao == "ADD":
        resultado = a + b
    elif operacao == "SUB":
        resultado = a - b
    elif operacao == "AND":
        resultado = a & b
    elif operacao == "OR":
        resultado = a | b
    elif operacao == "XOR":
        resultado = a ^ b
    else:
        raise ValueError(f"Operação da ULA inválida: {operacao}")
    return limitar_8bits(resultado)
