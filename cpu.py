"""
cpu.py - CPU simulada de 8 bits.

Componentes:
    - 4 registradores de 8 bits (R0..R3)
    - PC (contador de programa)
    - memória de 16 posições (cada posição guarda uma instrução em texto
      ou um valor numérico)
    - ULA (ver ula.py)

Ciclo de execução: FETCH -> DECODE -> EXECUTE.
"""

from ula import ula, limitar_8bits, OPERACOES_ULA

TAMANHO_MEMORIA = 16
REGISTRADORES = ("R0", "R1", "R2", "R3")

# Quantidade de operandos esperada por instrução
ARIDADE = {
    "LOAD": 2, "STORE": 2,
    "ADD": 2, "SUB": 2, "AND": 2, "OR": 2, "XOR": 2,
    "JMP": 1, "HALT": 0,
}


class CPU:
    def __init__(self):
        # Registradores gerais (8 bits cada)
        self.registradores = {nome: 0 for nome in REGISTRADORES}
        # Memória com 16 posições
        self.memoria = [0] * TAMANHO_MEMORIA
        # Program Counter
        self.pc = 0
        # Estado da CPU
        self.halted = False
        # Contador de ciclos executados
        self.ciclos = 0

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def limitar_8bits(self, valor):
        return limitar_8bits(valor)

    def carregar_programa(self, programa):
        """Copia a lista de instruções para o início da memória."""
        if len(programa) > TAMANHO_MEMORIA:
            raise ValueError(
                f"Programa com {len(programa)} instruções não cabe "
                f"na memória de {TAMANHO_MEMORIA} posições"
            )
        for endereco, instrucao in enumerate(programa):
            self.memoria[endereco] = instrucao

    @staticmethod
    def _validar_endereco(endereco):
        if not 0 <= endereco < TAMANHO_MEMORIA:
            raise ValueError(
                f"Endereço inválido: {endereco} "
                f"(use 0 a {TAMANHO_MEMORIA - 1})"
            )

    @staticmethod
    def _validar_registrador(nome):
        if nome not in REGISTRADORES:
            raise ValueError(f"Registrador inexistente: {nome}")

    @staticmethod
    def _inteiro(texto, descricao):
        try:
            return int(texto)
        except ValueError:
            raise ValueError(f"{descricao} inválido: {texto!r}") from None

    # ------------------------------------------------------------------
    # FETCH
    # ------------------------------------------------------------------
    def fetch(self):
        """Busca na memória a instrução apontada pelo PC."""
        self._validar_endereco(self.pc)
        instrucao = self.memoria[self.pc]
        if not isinstance(instrucao, str):
            raise ValueError(
                f"MEM[{self.pc}] contém o valor {instrucao}, "
                f"não uma instrução (falta um HALT?)"
            )
        return instrucao

    # ------------------------------------------------------------------
    # DECODE
    # ------------------------------------------------------------------
    def decode(self, instrucao):
        """Identifica a operação e seus operandos.

        Devolve (operacao, [operandos]) já validando a quantidade de
        operandos e os nomes de registradores.
        """
        partes = instrucao.replace(",", " ").split()
        if not partes:
            raise ValueError("Instrução vazia")
        operacao = partes[0].upper()
        operandos = partes[1:]

        if operacao not in ARIDADE:
            raise ValueError(f"Instrução desconhecida: {operacao}")
        if len(operandos) != ARIDADE[operacao]:
            raise ValueError(
                f"{operacao} espera {ARIDADE[operacao]} operando(s), "
                f"recebeu {len(operandos)}: {instrucao!r}"
            )
        operandos = [op.upper() if op.upper() in REGISTRADORES else op
                     for op in operandos]
        return operacao, operandos

    # ------------------------------------------------------------------
    # EXECUTE
    # ------------------------------------------------------------------
    def execute(self, operacao, operandos):
        """Executa a operação e atualiza registradores, memória ou PC."""
        if operacao == "LOAD":
            # LOAD R0, 5  -> R0 <- 5
            reg = operandos[0]
            self._validar_registrador(reg)
            valor = self._inteiro(operandos[1], "Valor")
            self.registradores[reg] = self.limitar_8bits(valor)
            self.pc += 1

        elif operacao == "STORE":
            # STORE R0, 15 -> MEM[15] <- R0
            reg = operandos[0]
            self._validar_registrador(reg)
            endereco = self._inteiro(operandos[1], "Endereço")
            self._validar_endereco(endereco)
            self.memoria[endereco] = self.registradores[reg]
            self.pc += 1

        elif operacao in OPERACOES_ULA:
            # ADD R0, R1 -> R0 <- R0 (op) R1
            destino, origem = operandos
            self._validar_registrador(destino)
            self._validar_registrador(origem)
            self.registradores[destino] = ula(
                operacao,
                self.registradores[destino],
                self.registradores[origem],
            )
            self.pc += 1

        elif operacao == "JMP":
            # JMP 8 -> PC <- 8
            endereco = self._inteiro(operandos[0], "Endereço")
            self._validar_endereco(endereco)
            self.pc = endereco

        elif operacao == "HALT":
            # O PC não avança: fica apontando para o HALT.
            self.halted = True

    def executar_instrucao(self, instrucao):
        """Decode + Execute de uma instrução em texto."""
        operacao, operandos = self.decode(instrucao)
        self.execute(operacao, operandos)

    # ------------------------------------------------------------------
    # CICLO DA CPU
    # ------------------------------------------------------------------
    def ciclo(self, verbose=True):
        """Executa um ciclo completo: Fetch -> Decode -> Execute."""
        # FETCH
        instrucao = self.fetch()
        if verbose:
            print()
            print("-----------------------------")
            print(f"PC: {self.pc:02d}")
            print(f"Instrução: {instrucao}")
            print(self.linha_registradores())
            print("Executando...")

        # DECODE
        operacao, operandos = self.decode(instrucao)

        # EXECUTE
        self.execute(operacao, operandos)
        self.ciclos += 1

        if verbose:
            if self.halted:
                print("CPU encerrada (HALT).")
            else:
                print(f"Depois -> PC: {self.pc:02d}  "
                      f"{self.linha_registradores(decimal=True)}")
        return instrucao

    def executar(self, passo_a_passo=False, limite_ciclos=1000, verbose=True):
        """Executa o programa até o HALT.

        passo_a_passo: espera ENTER a cada ciclo.
        limite_ciclos: evita laço infinito (ex.: JMP 0 sem HALT).
        """
        while not self.halted:
            if self.ciclos >= limite_ciclos:
                raise RuntimeError(
                    f"Limite de {limite_ciclos} ciclos atingido "
                    f"(possível laço infinito)"
                )
            self.ciclo(verbose=verbose)
            if passo_a_passo and not self.halted:
                try:
                    input("[ENTER] próximo ciclo...")
                except EOFError:
                    passo_a_passo = False

    # ------------------------------------------------------------------
    # VISUALIZAÇÃO
    # ------------------------------------------------------------------
    def linha_registradores(self, decimal=False):
        """Ex.: 'R0 = 05 R1 = 08 R2 = 00 R3 = 00' (valores em hexadecimal)."""
        if decimal:
            itens = [f"{n} = {v:02X} ({v})"
                     for n, v in self.registradores.items()]
        else:
            itens = [f"{n} = {v:02X}" for n, v in self.registradores.items()]
        return " ".join(itens)

    def mostrar_estado(self):
        print(f"PC: {self.pc:02d}")
        print(self.linha_registradores(decimal=True))

    def mostrar_memoria(self):
        print("Memória:")
        for endereco, conteudo in enumerate(self.memoria):
            print(f"  [{endereco:02d}] {conteudo}")
