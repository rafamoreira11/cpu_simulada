"""
testes.py - Testes automáticos da CPU simulada.

Execução:  python testes.py        (ou: python -m unittest testes -v)
"""

import unittest

from cpu import CPU
from ula import ula
from programas import PROGRAMA_EXEMPLO, PROGRAMA_PROPRIO, PROGRAMA_OVERFLOW


def rodar(programa, **kwargs):
    """Cria uma CPU, carrega o programa, executa em silêncio e a devolve."""
    cpu = CPU()
    cpu.carregar_programa(programa)
    cpu.executar(verbose=False, **kwargs)
    return cpu


class TestULA(unittest.TestCase):
    def test_add(self):
        self.assertEqual(ula("ADD", 5, 8), 13)

    def test_sub(self):
        self.assertEqual(ula("SUB", 8, 5), 3)

    def test_and(self):
        self.assertEqual(ula("AND", 0b1100, 0b1010), 0b1000)

    def test_or(self):
        self.assertEqual(ula("OR", 0b1100, 0b1010), 0b1110)

    def test_xor(self):
        self.assertEqual(ula("XOR", 0b1100, 0b1010), 0b0110)

    def test_add_overflow_8bits(self):
        self.assertEqual(ula("ADD", 200, 100), 44)
        self.assertEqual(ula("ADD", 255, 1), 0)

    def test_sub_underflow_8bits(self):
        self.assertEqual(ula("SUB", 3, 5), 254)
        self.assertEqual(ula("SUB", 0, 1), 255)

    def test_operacao_invalida(self):
        with self.assertRaises(ValueError):
            ula("MUL", 1, 2)


class TestInstrucoes(unittest.TestCase):
    def test_load(self):
        cpu = rodar(["LOAD R2, 42", "HALT"])
        self.assertEqual(cpu.registradores["R2"], 42)

    def test_load_limita_8bits(self):
        cpu = rodar(["LOAD R0, 300", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 44)

    def test_store(self):
        cpu = rodar(["LOAD R1, 77", "STORE R1, 10", "HALT"])
        self.assertEqual(cpu.memoria[10], 77)

    def test_store_nao_altera_registrador(self):
        cpu = rodar(["LOAD R1, 77", "STORE R1, 10", "HALT"])
        self.assertEqual(cpu.registradores["R1"], 77)

    def test_add(self):
        cpu = rodar(["LOAD R0, 5", "LOAD R1, 8", "ADD R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 13)
        self.assertEqual(cpu.registradores["R1"], 8)  # origem intacta

    def test_sub(self):
        cpu = rodar(["LOAD R0, 9", "LOAD R1, 4", "SUB R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 5)

    def test_sub_negativo_vira_8bits(self):
        cpu = rodar(["LOAD R0, 3", "LOAD R1, 5", "SUB R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 254)

    def test_add_overflow(self):
        cpu = rodar(["LOAD R0, 200", "LOAD R1, 100", "ADD R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 44)

    def test_and(self):
        cpu = rodar(["LOAD R0, 12", "LOAD R1, 10", "AND R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 8)

    def test_or(self):
        cpu = rodar(["LOAD R0, 12", "LOAD R1, 10", "OR R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 14)

    def test_xor(self):
        cpu = rodar(["LOAD R0, 12", "LOAD R1, 10", "XOR R0, R1", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 6)

    def test_operacao_com_registradores_diferentes(self):
        cpu = rodar(["LOAD R2, 20", "LOAD R3, 22", "ADD R2, R3", "HALT"])
        self.assertEqual(cpu.registradores["R2"], 42)

    def test_virgula_opcional(self):
        cpu = rodar(["LOAD R0 7", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 7)

    def test_instrucao_em_minusculas(self):
        cpu = rodar(["load r0, 7", "halt"])
        self.assertEqual(cpu.registradores["R0"], 7)


class TestControle(unittest.TestCase):
    def test_pc_avanca_uma_posicao(self):
        cpu = CPU()
        cpu.carregar_programa(["LOAD R0, 1", "LOAD R1, 2", "HALT"])
        self.assertEqual(cpu.pc, 0)
        cpu.ciclo(verbose=False)
        self.assertEqual(cpu.pc, 1)
        cpu.ciclo(verbose=False)
        self.assertEqual(cpu.pc, 2)

    def test_pc_avanca_em_todas_as_instrucoes_nao_jmp(self):
        for ins in ("LOAD R0, 1", "STORE R0, 5", "ADD R0, R1", "SUB R0, R1",
                    "AND R0, R1", "OR R0, R1", "XOR R0, R1"):
            cpu = CPU()
            cpu.carregar_programa([ins, "HALT"])
            cpu.ciclo(verbose=False)
            self.assertEqual(cpu.pc, 1, ins)

    def test_jmp_altera_pc(self):
        cpu = CPU()
        cpu.carregar_programa(["JMP 3", "LOAD R0, 1", "HALT", "HALT"])
        cpu.ciclo(verbose=False)
        self.assertEqual(cpu.pc, 3)

    def test_jmp_pula_instrucoes(self):
        cpu = rodar(["JMP 3", "LOAD R0, 1", "HALT", "LOAD R1, 7", "HALT"])
        self.assertEqual(cpu.registradores["R0"], 0)
        self.assertEqual(cpu.registradores["R1"], 7)

    def test_halt_interrompe(self):
        cpu = rodar(["LOAD R0, 1", "HALT", "LOAD R0, 99"])
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.registradores["R0"], 1)
        self.assertEqual(cpu.pc, 1)
        self.assertEqual(cpu.ciclos, 2)

    def test_halt_isolado(self):
        cpu = rodar(["HALT"])
        self.assertTrue(cpu.halted)
        self.assertEqual(cpu.ciclos, 1)


class TestProgramas(unittest.TestCase):
    def test_programa_exemplo(self):
        cpu = rodar(PROGRAMA_EXEMPLO)
        self.assertEqual(cpu.memoria[15], 13)
        self.assertEqual(cpu.ciclos, 5)

    def test_programa_proprio(self):
        cpu = rodar(PROGRAMA_PROPRIO)
        self.assertGreaterEqual(len(PROGRAMA_PROPRIO), 8)
        self.assertEqual(cpu.memoria[14], 6)
        self.assertEqual(cpu.memoria[15], 2)
        self.assertEqual(cpu.registradores["R3"], 0)  # LOAD R3 foi pulado
        self.assertEqual(cpu.ciclos, 11)  # 12 instruções, 1 pulada

    def test_programa_overflow(self):
        cpu = rodar(PROGRAMA_OVERFLOW)
        self.assertEqual(cpu.memoria[14], 44)
        self.assertEqual(cpu.memoria[15], 254)

    def test_resultados_sempre_8_bits(self):
        for prog in (PROGRAMA_EXEMPLO, PROGRAMA_PROPRIO, PROGRAMA_OVERFLOW):
            cpu = rodar(prog)
            for valor in cpu.registradores.values():
                self.assertTrue(0 <= valor <= 255)
            for conteudo in cpu.memoria:
                if isinstance(conteudo, int):
                    self.assertTrue(0 <= conteudo <= 255)


class TestErros(unittest.TestCase):
    def test_instrucao_desconhecida(self):
        with self.assertRaises(ValueError):
            rodar(["MUL R0, R1", "HALT"])

    def test_registrador_inexistente(self):
        with self.assertRaises(ValueError):
            rodar(["LOAD R9, 1", "HALT"])

    def test_endereco_store_invalido(self):
        with self.assertRaises(ValueError):
            rodar(["LOAD R0, 1", "STORE R0, 16", "HALT"])

    def test_endereco_jmp_invalido(self):
        with self.assertRaises(ValueError):
            rodar(["JMP 20"])

    def test_operandos_faltando(self):
        with self.assertRaises(ValueError):
            rodar(["ADD R0", "HALT"])

    def test_programa_sem_halt(self):
        # O PC chega a uma posição que contém dado (0), não instrução
        with self.assertRaises(ValueError):
            rodar(["LOAD R0, 1"])

    def test_laco_infinito_e_interrompido(self):
        with self.assertRaises(RuntimeError):
            rodar(["JMP 0"], limite_ciclos=50)

    def test_programa_maior_que_memoria(self):
        cpu = CPU()
        with self.assertRaises(ValueError):
            cpu.carregar_programa(["HALT"] * 17)


if __name__ == "__main__":
    unittest.main(verbosity=2)
