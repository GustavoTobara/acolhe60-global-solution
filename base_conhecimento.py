"""
Classe BaseConhecimento: lê o JSON, lista as categorias e busca a melhor orientação.
"""

import json
import unicodedata

from orientacao import Orientacao

# palavras que não ajudam a achar o assunto
PALAVRAS_VAZIAS = {"para", "como", "onde", "quero", "queria", "preciso", "minha", "meus",
                   "minhas", "voce", "isso", "esse", "essa", "tenho", "sobre", "fazer",
                   "posso", "pode", "qual", "quais", "quando", "estou", "anos"}

PONTOS_FRASE = 4      # palavra-chave com 2 ou mais palavras encontrada inteira
PONTOS_PALAVRA = 2    # palavra-chave de uma palavra encontrada
PONTOS_TITULO = 1     # palavra da pergunta (4+ letras) que aparece no título

LIMITE_ALTA = 7
LIMITE_MEDIA = 4


def normalizar(texto):
    """minúsculas, sem acento e sem pontuação, com um espaço nas pontas"""
    decomposto = unicodedata.normalize("NFD", str(texto).lower())
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    limpo = "".join(c if c.isalnum() else " " for c in sem_acento)
    return " " + " ".join(limpo.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho, caminho_apoio):
        self.caminho = caminho
        self.caminho_apoio = caminho_apoio
        self.orientacoes = []
        self.frases_sinonimas = []    # lista de tuplas (variante, forma padrão)
        self.palavras_sinonimas = {}  # dicionário variante -> forma padrão
        self.telefones = []
        self.avisos = []

    # ---------- leitura dos arquivos ----------

    def carregar(self):
        self._carregar_apoio()
        try:
            with open(self.caminho, encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
        except FileNotFoundError:
            self.avisos.append("Base de conhecimento não encontrada. O assistente vai funcionar sem orientações.")
            return
        except json.JSONDecodeError:
            self.avisos.append("A base de conhecimento está com erro de formato. Nenhuma orientação carregada.")
            return

        ignoradas = 0
        for dados in registros:
            try:
                orientacao = Orientacao.de_dicionario(dados)
            except (KeyError, ValueError, TypeError):
                ignoradas += 1
                continue
            # guarda as palavras-chave e o título já preparados para a comparação
            orientacao.chaves_prontas = [self.preparar(p).strip() for p in orientacao.palavras_chave]
            orientacao.palavras_titulo = set(self.preparar(orientacao.titulo).split())
            self.orientacoes.append(orientacao)
        if ignoradas:
            self.avisos.append(f"{ignoradas} orientação(ões) incompleta(s) foram ignoradas.")

    def _carregar_apoio(self):
        try:
            with open(self.caminho_apoio, encoding="utf-8") as arquivo:
                apoio = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.avisos.append("Arquivo de sinônimos não encontrado. A busca vai usar só as palavras exatas.")
            return

        for padrao, variantes in apoio.get("sinonimos", {}).items():
            padrao = normalizar(padrao).strip()
            for variante in variantes:
                variante = normalizar(variante).strip()
                if variante == padrao:
                    continue
                if " " in variante:
                    self.frases_sinonimas.append((variante, padrao))
                else:
                    self.palavras_sinonimas[variante] = padrao
        # frases maiores primeiro: "pressao alta" antes de "pressao"
        self.frases_sinonimas.sort(key=lambda par: len(par[0]), reverse=True)
        self.telefones = apoio.get("telefones", [])

    # ---------- preparação do texto ----------

    def preparar(self, texto):
        """normaliza e troca cada sinônimo pela forma padrão"""
        texto = normalizar(texto)
        for variante, padrao in self.frases_sinonimas:
            texto = texto.replace(" " + variante + " ", " " + padrao + " ")
        palavras = [self.palavras_sinonimas.get(p, p) for p in texto.split()]
        return " " + " ".join(palavras) + " "

    # ---------- consultas ----------

    def categorias(self):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def por_id(self, id):
        for orientacao in self.orientacoes:
            if orientacao.id == id:
                return orientacao
        return None

    def pontuar(self, pergunta_pronta, orientacao):
        """devolve (pontos, motivos) de uma orientação para a pergunta já preparada"""
        pontos = 0
        motivos = []
        palavras = set(pergunta_pronta.split())

        for chave in orientacao.chaves_prontas:
            if " " in chave:
                if " " + chave + " " in pergunta_pronta:
                    pontos += PONTOS_FRASE
                    motivos.append(chave)
            elif chave in palavras:
                pontos += PONTOS_PALAVRA
                motivos.append(chave)

        for palavra in palavras:
            if len(palavra) >= 4 and palavra not in PALAVRAS_VAZIAS \
                    and palavra in orientacao.palavras_titulo and palavra not in motivos:
                pontos += PONTOS_TITULO
                motivos.append(palavra)
        return pontos, motivos

    def buscar(self, pergunta):
        """lista de tuplas (pontos, orientacao), da maior pontuação para a menor"""
        pronta = self.preparar(pergunta)
        resultado = []
        for orientacao in self.orientacoes:
            pontos, _ = self.pontuar(pronta, orientacao)
            if pontos > 0:
                resultado.append((pontos, orientacao))
        resultado.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultado

    def motivos(self, pergunta, orientacao):
        return self.pontuar(self.preparar(pergunta), orientacao)[1]

    @staticmethod
    def confianca(pontos):
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None
