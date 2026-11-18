"""
Classe Assistente: conversa com a pessoa, guarda o histórico,
calcula os indicadores e exporta o CSV.
"""

import csv
import json
import os
import re
import time
from datetime import datetime

MAX_TENTATIVAS = 3

# sinais de golpe (já na forma padrão dos sinônimos)
SINAIS_GOLPE = {"pix", "codigo", "link", "ligaram", "whatsapp", "sms", "mensagem",
                "pediram", "pedindo", "pediu", "deposito", "transferencia", "boleto", "taxa"}
CONTEXTO_GOLPE = {"inss", "banco", "beneficio", "aposentadoria", "aposentado",
                  "emprestimo", "cartao", "conta", "senha"}

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou",
              "tentativas", "tempo_segundos", "alerta_golpe", "nota"]


# ---------- leitura segura do teclado ----------

def ler_opcao(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        print(f"  Opção inválida. Digite um número de {minimo} a {maximo}.")


def ler_sim_nao(mensagem):
    while True:
        resposta = input(mensagem + " (s/n): ").strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("  Responda s para sim ou n para não.")


class Assistente:
    def __init__(self, nome, base, caminho_historico, caminho_csv):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = []
        self.atendimentos_da_sessao = []
        self.leitura_facil = False
        self.carregar_historico()

    # ---------- histórico ----------

    def carregar_historico(self):
        try:
            with open(self.caminho_historico, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return
        except json.JSONDecodeError:
            print("[aviso] historico.json estava com erro de formato. Começando um histórico novo.")
            return
        if isinstance(dados, list):
            self.historico = [r for r in dados if isinstance(r, dict) and "encontrou" in r]

    def salvar_historico(self):
        pasta = os.path.dirname(self.caminho_historico)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
            json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)

    def registrar(self, origem, pergunta, orientacao, ajudou, tentativas, inicio, alerta):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao else None,
            "encontrou": orientacao is not None,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
            "alerta_golpe": alerta,
            "nota": None,  # preenchida ao sair
        }
        self.historico.append(atendimento)
        self.atendimentos_da_sessao.append(atendimento)
        self.salvar_historico()

    # ---------- verificações da pergunta ----------

    @staticmethod
    def tem_dado_pessoal(texto):
        """pergunta com @ ou com 8 ou mais dígitos é recusada"""
        if "@" in texto:
            return True
        so_numeros = re.sub(r"[\s.\-/()]", "", texto)
        return re.search(r"\d{8,}", so_numeros) is not None

    def parece_golpe(self, pergunta):
        palavras = set(self.base.preparar(pergunta).split())
        if "golpe" in palavras:
            return True
        sinais = len(palavras & SINAIS_GOLPE)
        contexto = len(palavras & CONTEXTO_GOLPE)
        return sinais >= 2 or (sinais >= 1 and contexto >= 1)

    @staticmethod
    def alerta_golpe():
        print("\n" + "!" * 64)
        print("  CUIDADO: sua pergunta tem sinais de GOLPE.")
        print("  O INSS e os bancos não pedem senha, código, PIX ou dados por")
        print("  telefone, mensagem ou visita. Não passe nada. Na dúvida, ligue 135.")
        print("!" * 64)

    # ---------- opção 1: pergunta em texto livre ----------

    def perguntar(self):
        print("\nEscreva sua dúvida do seu jeito. Exemplo: 'quero andar de ônibus de graça'")
        print("Não escreva nome, CPF, telefone ou e-mail.")
        inicio = time.time()
        tentativas = 0
        ultima = ""
        orientacao = None
        ajudou = False
        alerta = False

        while tentativas < MAX_TENTATIVAS:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                break
            if len(pergunta) < 3:
                print("Escreva pelo menos uma palavra com 3 letras.")
                continue
            if self.tem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva sem esses dados.")
                continue

            tentativas += 1
            ultima = pergunta
            if self.parece_golpe(pergunta):
                alerta = True
                self.alerta_golpe()

            orientacao, ajudou = self._responder(pergunta, alerta)
            if ajudou:
                break
            if tentativas < MAX_TENTATIVAS and not ler_sim_nao("Quer tentar com outras palavras?"):
                break

        if tentativas == 0:
            return
        self.registrar("pergunta", ultima, orientacao, ajudou, tentativas, inicio, alerta)

    def _responder(self, pergunta, alerta):
        resultado = self.base.buscar(pergunta)
        achou = len(resultado) > 0 and self.base.confianca(resultado[0][0]) is not None

        if not achou and alerta:
            # sem orientação certa, mas com cara de golpe: mostra a ficha de proteção
            protecao = self.base.por_id(13)
            if protecao:
                print("\nNão achei o assunto exato, mas veja como se proteger:")
                protecao.exibir(self.leitura_facil)
                return protecao, ler_sim_nao("\nEssa orientação respondeu sua dúvida?")

        if not achou:
            print("\nNão encontrei uma orientação para essa dúvida.")
            print("Tente palavras simples, como 'remédio', 'ônibus', 'aposentadoria' ou 'golpe'.")
            print("Ou escolha pela categoria: " + ", ".join(self.base.categorias()))
            return None, False

        pontos, melhor = resultado[0]
        print(f"\nConfiança da resposta: {self.base.confianca(pontos)} ({pontos} pontos)")
        print("Palavras que levaram a esta resposta: " + ", ".join(self.base.motivos(pergunta, melhor)))
        melhor.exibir(self.leitura_facil)
        if ler_sim_nao("\nEssa orientação respondeu sua dúvida?"):
            return melhor, True

        alternativas = [o for p, o in resultado[1:3] if self.base.confianca(p) is not None]
        if not alternativas:
            return melhor, False
        print("\nTalvez seja uma destas:")
        for numero, outra in enumerate(alternativas, start=1):
            print(f"  {numero} - {outra.titulo}")
        print("  0 - Nenhuma destas")
        escolha = ler_opcao("Escolha: ", 0, len(alternativas))
        if escolha == 0:
            return melhor, False
        escolhida = alternativas[escolha - 1]
        escolhida.exibir(self.leitura_facil)
        return escolhida, ler_sim_nao("\nEssa orientação respondeu sua dúvida?")

    # ---------- opção 2: navegação por categorias ----------

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento está vazia.")
            return
        inicio = time.time()
        while True:
            print("\nCATEGORIAS")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero} - {categoria}")
            print("  0 - Voltar")
            escolha = ler_opcao("Escolha a categoria: ", 0, len(categorias))
            if escolha == 0:
                return

            orientacoes = self.base.por_categoria(categorias[escolha - 1])
            print(f"\n{categorias[escolha - 1].upper()}")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero} - {orientacao.titulo}")
            print("  0 - Voltar às categorias")
            item = ler_opcao("Escolha a orientação: ", 0, len(orientacoes))
            if item == 0:
                continue

            orientacao = orientacoes[item - 1]
            orientacao.exibir(self.leitura_facil)
            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida?")
            descricao = f"[categoria] {orientacao.categoria} > {orientacao.titulo}"
            self.registrar("categoria", descricao, orientacao, ajudou, 1, inicio, False)
            return

    # ---------- extras do Acolhe 60+ ----------

    def telefones(self):
        print("\nTELEFONES ÚTEIS (ligação gratuita)")
        for numero, servico, horario in self.base.telefones:
            extra = f" - {horario}" if horario else ""
            print(f"  {numero:>4}  {servico}{extra}")

    def alternar_leitura_facil(self):
        self.leitura_facil = not self.leitura_facil
        if self.leitura_facil:
            print("\nLeitura fácil LIGADA: os passos aparecem um de cada vez (aperte Enter).")
        else:
            print("\nLeitura fácil DESLIGADA.")

    # ---------- indicadores e CSV ----------

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return

        encontrados = [a for a in self.historico if a["encontrou"]]
        ajudaram = [a for a in self.historico if a["ajudou"]]
        notas = [a["nota"] for a in self.historico if a.get("nota")]
        tempo_medio = sum(a["tempo_segundos"] for a in encontrados) / len(encontrados) if encontrados else 0
        tentativas = sum(a["tentativas"] for a in self.historico) / total

        print(f"\nINDICADORES DO {self.nome.upper()}")
        print(f"  Total de atendimentos ........... {total}")
        print(f"  Resposta encontrada ............. {100 * len(encontrados) / total:.1f}%")
        print(f"  Taxa de acerto (ajudou) ......... {100 * len(ajudaram) / total:.1f}%")
        print(f"  Tempo médio para encontrar ...... {tempo_medio:.1f} s")
        print(f"  Tentativas por atendimento ...... {tentativas:.1f}")
        if notas:
            print(f"  Facilidade de uso (1 a 5) ....... {sum(notas) / len(notas):.1f}")
        else:
            print("  Facilidade de uso (1 a 5) ....... sem notas ainda")
        print(f"  Alertas de golpe mostrados ...... {sum(1 for a in self.historico if a.get('alerta_golpe'))}")

        print("\n  Dúvidas sem solução:")
        sem_solucao = [a["pergunta"] for a in self.historico
                       if a["origem"] == "pergunta" and not a["ajudou"]]
        if not sem_solucao:
            print("    nenhuma")
        for pergunta in sem_solucao:
            print(f'    - "{pergunta}"')

    def exportar_csv(self):
        pasta = os.path.dirname(self.caminho_csv)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, delimiter=";")
            escritor.writeheader()
            for atendimento in self.historico:
                escritor.writerow({campo: atendimento.get(campo, "") for campo in CAMPOS_CSV})
        print(f"\n{len(self.historico)} atendimento(s) exportado(s) para {self.caminho_csv}")

    # ---------- saída ----------

    def encerrar(self):
        if self.atendimentos_da_sessao:
            nota = ler_opcao("\nDe 1 (muito difícil) a 5 (muito fácil), como foi usar o assistente? ", 1, 5)
            for atendimento in self.atendimentos_da_sessao:
                atendimento["nota"] = nota
            self.salvar_historico()
        print("\nAté logo! Na dúvida, confira sempre no canal oficial.")
