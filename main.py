"""
main.py - Execução e visualização passo a passo da CPU simulada.

Uso:
    python main.py                      # programa do enunciado, contínuo
    python main.py --programa proprio   # programa próprio do grupo
    python main.py --passo              # espera ENTER a cada ciclo
    python main.py --programa overflow --passo
"""

import argparse

from cpu import CPU
from programas import PROGRAMAS


def main():
    parser = argparse.ArgumentParser(description="CPU simulada de 8 bits")
    parser.add_argument("--programa", choices=PROGRAMAS.keys(),
                        default="exemplo", help="programa a executar")
    parser.add_argument("--passo", action="store_true",
                        help="modo passo a passo (ENTER a cada ciclo)")
    args = parser.parse_args()

    cpu = CPU()
    programa = PROGRAMAS[args.programa]
    cpu.carregar_programa(programa)

    print("================================")
    print(" CPU SIMULADA - 8 BITS")
    print("================================")
    print(f"Programa: {args.programa} ({len(programa)} instruções)")
    for endereco, instrucao in enumerate(programa):
        print(f"  [{endereco:02d}] {instrucao}")

    cpu.executar(passo_a_passo=args.passo)

    print()
    print("================================")
    print(f"Ciclos executados: {cpu.ciclos}")
    print("Estado final:")
    cpu.mostrar_estado()
    print()
    print("Memória[14]:", cpu.memoria[14])
    print("Memória[15]:", cpu.memoria[15])


if __name__ == "__main__":
    main()
