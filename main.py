"""
Global Solution 2026.2 - Pensamento Computacional e Automação com Python
Acolhe 60+ - assistente de orientação para pessoas idosas
Turma 1CCPY - FIAP
Gustavo Naville Tobara - RM 570674
Guilherme Marques dos Santos - RM 573112
Pedro Henrique Silva Santos - RM 571537
"""

import os

from assistente import Assistente, ler_opcao
from base_conhecimento import BaseConhecimento

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA, "data")


def main():
    base = BaseConhecimento(os.path.join(PASTA_DADOS, "base_conhecimento.json"),
                            os.path.join(PASTA_DADOS, "apoio.json"))
    base.carregar()  # lê o JSON e cria os objetos Orientacao
    for aviso in base.avisos:
        print(f"[aviso] {aviso}")

    assistente = Assistente("Acolhe 60+", base,
                            os.path.join(PASTA_DADOS, "historico.json"),
                            os.path.join(PASTA_DADOS, "atendimentos.csv"))

    print("=" * 64)
    print("  ACOLHE 60+")
    print("  Orientação sobre direitos e serviços para pessoas idosas")
    print(f"  {len(base.orientacoes)} orientações conferidas em fontes oficiais")
    print("=" * 64)

    opcoes = (
        ("Fazer uma pergunta", assistente.perguntar),
        ("Navegar por categorias", assistente.navegar),
        ("Telefones úteis", assistente.telefones),
        ("Ligar/desligar leitura fácil (um passo por vez)", assistente.alternar_leitura_facil),
        ("Ver indicadores", assistente.indicadores),
        ("Exportar atendimentos (CSV)", assistente.exportar_csv),
    )

    while True:
        print("\nMENU")
        for numero, (nome, _) in enumerate(opcoes, start=1):
            print(f"  {numero} - {nome}")
        print("  0 - Sair")
        escolha = ler_opcao("Digite a opção: ", 0, len(opcoes))
        if escolha == 0:
            assistente.encerrar()
            break
        opcoes[escolha - 1][1]()


if __name__ == "__main__":
    main()
