"""
Classe Orientacao: um registro da base de conhecimento (um dicionário do JSON).
"""

AVISO = "Aviso: este assistente NÃO é canal oficial. Confira sempre na fonte."

CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em")


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta, documentos,
                 onde, fonte, verificado_em, publico="", passos=None, telefone="", atencao=""):
        # campos obrigatórios do enunciado
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em
        # campos extras do Acolhe 60+
        self.publico = publico
        self.passos = passos or []
        self.telefone = telefone
        self.atencao = atencao

    @classmethod
    def de_dicionario(cls, dados):
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in dados:
                raise KeyError(campo)
        if len(dados["palavras_chave"]) < 3:
            raise ValueError("cada orientação precisa de pelo menos 3 palavras-chave")
        return cls(int(dados["id"]), dados["categoria"], dados["titulo"], dados["palavras_chave"],
                   dados["resposta"], dados["documentos"], dados["onde"], dados["fonte"],
                   dados["verificado_em"], dados.get("publico", ""), dados.get("passos", []),
                   dados.get("telefone", ""), dados.get("atencao", ""))

    def exibir(self, leitura_facil=False):
        print()
        print("#" * 64)
        print(f"  >> {self.titulo.upper()}  [{self.categoria}]")
        if self.publico:
            print(f"  Para quem: {self.publico}")
        print("#" * 64)
        print(f"\n{self.resposta}\n")

        if self.passos:
            print("PASSO A PASSO")
            for numero, passo in enumerate(self.passos, start=1):
                print(f"  {numero}. {passo}")
                if leitura_facil and numero < len(self.passos):
                    input("     (aperte Enter para o próximo passo)\n")

        print("\nDOCUMENTOS NECESSÁRIOS")
        for documento in self.documentos:
            print(f"  [ ] {documento}")

        print(f"\nONDE: {self.onde}")
        if self.telefone:
            print(f"TELEFONE: {self.telefone}")
        if self.atencao:
            print(f"\n(!) ATENÇÃO: {self.atencao}")
        print(f"\nFonte: {self.fonte} (verificado em {self.verificado_em})")
        print(AVISO)
        print("#" * 64)
