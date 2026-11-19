# Acolhe 60+ — Assistente de orientação para pessoas idosas

**Global Solution 2026.2 · Pensamento Computacional e Automação com Python · FIAP · Turma 1CCPY**

## Integrantes

| Nome | RM |
|---|---|
| Gustavo Naville Tobara | 570674 |
| Guilherme Marques dos Santos | 573112 |
| Pedro Henrique Silva Santos | 571537 |

## Vídeo técnico

[Assistir ao vídeo técnico](https://youtu.be/cLyxrN1vrAA)

## Público e problema

**Público:** pessoas com 60 anos ou mais da Grande São Paulo e quem cuida delas.

**Problema:** muitos direitos da pessoa idosa dependem hoje de aplicativo, conta gov.br ou de saber o caminho certo: remédio e fralda de graça na Farmácia Popular, ônibus gratuito, BPC, prova de vida, Carteira da Pessoa Idosa. Ao mesmo tempo, essa faixa de idade é uma das mais visadas por golpes que imitam o INSS e os bancos. Quem não sabe onde perguntar deixa de usar um direito ou cai numa mensagem falsa.

**Solução:** o Acolhe 60+ é um assistente de terminal que responde à dúvida escrita do jeito que a pessoa fala ("quero andar de ônibus sem pagar") ou por categorias numeradas. Cada resposta traz:

- o passo a passo;
- os documentos necessários;
- onde ir e o telefone;
- a fonte oficial e a data de verificação;
- o aviso de que o assistente não é canal oficial.

O assistente também **reconhece sinais de golpe** na pergunta e mostra um alerta antes da resposta. Tem ainda um modo de **leitura fácil**, que mostra um passo de cada vez.

## ODS relacionados

- **ODS 3 – Saúde e bem-estar:** remédio e fralda gratuitos pela Farmácia Popular e vacina da gripe para 60+.
- **ODS 10 – Redução das desigualdades:** informação em linguagem simples para quem tem mais dificuldade com serviços digitais.
- **ODS 11 – Cidades e comunidades sustentáveis (meta 11.2, transporte acessível):** gratuidade em ônibus, metrô e trem e nas viagens entre estados.
- **ODS 16 – Paz, justiça e instituições eficazes:** caminho para denunciar violência contra a pessoa idosa, proteção contra golpes e direcionamento aos canais oficiais.

## Como executar

Requisito: **Python 3.8 ou mais novo**. Não usa bibliotecas externas.

```
python main.py
```

Menu:

```
1 - Fazer uma pergunta
2 - Navegar por categorias
3 - Telefones úteis
4 - Ligar/desligar leitura fácil (um passo por vez)
5 - Ver indicadores
6 - Exportar atendimentos (CSV)
0 - Sair
```

## Estrutura do projeto

```
acolhe60/
├── README.md
├── main.py                 → ponto de entrada e menu
├── orientacao.py           → classe Orientacao
├── base_conhecimento.py    → classe BaseConhecimento e função normalizar()
├── assistente.py           → classe Assistente (atendimento, histórico, indicadores e CSV)
└── data/
    ├── base_conhecimento.json   → 13 orientações em 5 categorias
    ├── apoio.json               → dicionário de sinônimos e telefones úteis
    ├── historico.json           → atendimentos registrados
    └── atendimentos.csv         → criado pela opção 6
```

## Classes e composição

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em, e os extras publico, passos, telefone, atencao | `de_dicionario()`, `exibir()` |
| `BaseConhecimento` | caminho, caminho_apoio, orientacoes, frases_sinonimas, palavras_sinonimas, telefones, avisos | `carregar()`, `preparar()`, `categorias()`, `por_categoria()`, `por_id()`, `pontuar()`, `buscar()`, `motivos()`, `confianca()` |
| `Assistente` | nome, base, historico, caminho_historico, caminho_csv, atendimentos_da_sessao, leitura_facil | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `tem_dado_pessoal()`, `parece_golpe()`, `telefones()`, `alternar_leitura_facil()`, `encerrar()` |

As classes se encaixam por **composição**:

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, Orientacao, ...]
```

No `main.py`:

```python
base = BaseConhecimento("data/base_conhecimento.json", "data/apoio.json")
base.carregar()          # lê o JSON e cria os objetos Orientacao
assistente = Assistente("Acolhe 60+", base, "data/historico.json", "data/atendimentos.csv")
assistente.perguntar()   # usa base.buscar() e orientacao.exibir()
```

## Base de conhecimento

`data/base_conhecimento.json` é uma **lista de dicionários**, um por orientação, com todos os campos obrigatórios do enunciado: `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`. Para o público idoso, acrescentamos quatro campos: `publico`, `passos` (passo a passo numerado), `telefone` e `atencao`. São **13 orientações em 5 categorias**:

| Categoria | Orientações |
|---|---|
| Documentos e direitos | 1 Carteira da Pessoa Idosa · 2 Atendimento prioritário (fila preferencial, prioridade especial 80+) |
| INSS e benefícios | 3 BPC para 65+ · 4 Prova de vida · 5 Bloquear benefício para empréstimo consignado · 6 Entrar no Meu INSS e na conta gov.br |
| Saúde | 7 Remédio grátis na Farmácia Popular · 8 Fralda geriátrica grátis · 9 Vacina da gripe |
| Transporte | 10 Ônibus, metrô e trem grátis em SP · 11 Viagem grátis para outro estado |
| Proteção e segurança | 12 Denunciar violência contra a pessoa idosa (Disque 100) · 13 Ligação ou mensagem suspeita (golpes) |

Cada orientação tem pelo menos 3 palavras-chave, uma fonte oficial e a data em que a equipe conferiu a informação. O `data/apoio.json` guarda o **dicionário de sinônimos** e os **telefones úteis**.

## Regra de pontuação (busca inteligente por regras)

1. **Normalização** (`normalizar()`): minúsculas, acentos removidos com `unicodedata`, toda pontuação trocada por espaço e um espaço em cada ponta do texto.
2. **Sinônimos** (`preparar()`): cada palavra ou expressão é trocada pela forma padrão do `apoio.json`. "Medicamento", "comprimido" e "remédios" viram `remedio`. "Zap" vira `whatsapp`. "De graça", "sem pagar" e "gratuito" viram `gratis`. "Busão" vira `onibus`. "Maus tratos" e "abandono" viram `violencia`. As palavras-chave e o título passam pela mesma preparação quando a base é carregada.
3. **Pontuação** (`pontuar()`). Ajustamos os pesos do enunciado (+3/+1) para dar mais peso às frases inteiras:

| Regra | Pontos |
|---|---|
| Palavra-chave de 2 ou mais palavras encontrada inteira na pergunta | +4 |
| Palavra-chave de 1 palavra encontrada na pergunta | +2 |
| Palavra da pergunta com 4 letras ou mais (fora da lista de palavras vazias) que aparece no título | +1 |

Motivo do ajuste: frases como "prova de vida" ou "cartão do ônibus" quase nunca aparecem por acaso. Palavras soltas como "inss" ou "banco" aparecem em muitos assuntos e não devem decidir sozinhas.

4. **Confiança** (`confianca()`):

| Pontuação da melhor orientação | Resultado |
|---|---|
| 7 ou mais | Confiança ALTA |
| 4 a 6 | Confiança MÉDIA |
| Menos de 4 | "Não encontrei": sugere palavras simples e as categorias |

`buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação, **as palavras que levaram até ela** e, se a pessoa disser que não ajudou, até **duas alternativas** com confiança média ou alta. A pessoa pode reescrever a dúvida até **3 vezes** no mesmo atendimento.

**Exemplo:** "Quero andar de ônibus sem pagar" vira `quero andar de onibus gratis`. A orientação 10 recebe:

- +2 por `onibus`;
- +4 por `onibus gratis`;
- +4 por `andar de onibus`;
- +1 porque `gratis` está no título ("Ônibus, metrô e trem de graça", com "de graça" convertido em `gratis`).

Total: **11 pontos, confiança ALTA**.

## Alerta de golpe

Antes de responder, `parece_golpe()` procura na pergunta já preparada:

- a palavra `golpe` (ou fraude, enganaram, falso), **ou**
- 2 sinais de golpe (pix, código, link, ligaram, mensagem, pediram, depósito, boleto, taxa…), **ou**
- 1 sinal de golpe junto com uma palavra de contexto (INSS, banco, benefício, aposentadoria, empréstimo, conta, senha).

Quando a regra dispara, aparece um quadro de alerta. Se nenhuma orientação passar de 4 pontos, o assistente mostra a orientação de golpes. "Esqueci a senha do meu INSS" **não** dispara o alerta, porque não tem nenhum sinal de golpe. "Pediram minha senha do banco por telefone" dispara.

## Regras de atendimento

- **Navegação:** categorias e orientações numeradas, com "0 para voltar" em todas as telas.
- **Entradas inválidas:** letras, números fora da faixa, texto vazio e s/n errado nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Perguntas com `@` ou com 8 ou mais dígitos seguidos (ignorando ponto, traço e espaço) são recusadas, **não contam como tentativa e não são registradas**.
- **Transparência:** toda resposta mostra a fonte, a data de verificação e o aviso "este assistente NÃO é canal oficial".
- **Arquivos:** se a base, os sinônimos ou o histórico estiverem ausentes ou corrompidos, o programa avisa e continua funcionando. Orientações sem algum campo obrigatório são ignoradas e contadas no aviso.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` assim que termina, como um dicionário com estes campos:

| Campo | Conteúdo |
|---|---|
| `data` | data e hora do atendimento |
| `origem` | `pergunta` ou `categoria` |
| `pergunta` | texto digitado (ou a categoria escolhida) |
| `id_orientacao` | id da orientação mostrada |
| `encontrou` | se achou uma orientação |
| `ajudou` | se a pessoa disse que resolveu |
| `tentativas` | quantas vezes escreveu a dúvida |
| `tempo_segundos` | `round(time.time() - inicio, 1)` |
| `alerta_golpe` | se o alerta apareceu |
| `nota` | facilidade de 1 a 5, pedida ao sair e gravada em todos os atendimentos da sessão |

Indicadores (opção 5):

- Resposta encontrada (%)
- Taxa de acerto: ajudou (%)
- Tempo médio para encontrar (s)
- Tentativas por atendimento
- Facilidade de uso (1 a 5)
- Alertas de golpe mostrados
- Lista de dúvidas sem solução

A opção 6 exporta para `data/atendimentos.csv` com `csv.DictWriter`. O arquivo usa separador `;` e codificação `utf-8-sig`, para abrir no Excel com os acentos certos.

## Testes internos da busca

Antes do teste com usuários, rodamos 16 perguntas escritas como uma pessoa idosa falaria. Todas foram para a orientação certa, e "Qual a previsão do tempo amanhã?" volta corretamente como "não encontrei". Ajustes feitos nesses testes:

| Pergunta | Problema | Ajuste |
|---|---|---|
| "Apareceu um empréstimo consignado que eu não fiz" | 3 pontos, caía em "não encontrei" | Palavras-chave `nao fiz`, `nao contratei`, `nao pedi` e `emprestimo no meu nome` na orientação 5. Passou para 6 pontos. |
| "Esqueci a senha do meu INSS" | Disparava alerta de golpe | "Senha" deixou de ser sinal de golpe e virou só palavra de contexto. |
| "Pediram minha senha do banco por telefone" | Alerta aparecia, mas não achava orientação | Palavras-chave `pediram minha senha` e `senha do banco` na orientação 13. O assistente também passou a mostrar a orientação 13 quando há alerta e nenhuma resposta. |
| "Me mandaram mensagem no zap pra atualizar o cadastro do benefício" | Não encontrava | Sinônimo `zap` → `whatsapp` e palavras-chave `atualizar o cadastro` e `mandaram mensagem`. Passou para 12 pontos. |

## Teste com usuários

> **A PREENCHER PELO GRUPO** depois do teste com pelo menos 3 pessoas de fora da equipe, somando 10 atendimentos ou mais. Não registrar nomes nem dados dos participantes.

**Como foi feito:**

**Indicadores obtidos (opção 5 do menu):**

| Indicador | Resultado |
|---|---|
| Total de atendimentos | |
| Resposta encontrada (%) | |
| Taxa de acerto: ajudou (%) | |
| Tempo médio para encontrar (s) | |
| Tentativas por atendimento | |
| Facilidade de uso (1 a 5) | |
| Alertas de golpe mostrados | |

**Dúvidas sem solução:**

**Análise:**

**Melhoria feita a partir do teste:** (palavra-chave ou sinônimo incluído no JSON, com os pontos antes e depois)

## Integração com outras disciplinas

Não há integração de código. O tema é o mesmo do projeto do grupo em **Data Structures and Algorithms**, o Acolhe 60+ de triagem e fila de chamados de pessoas idosas, com lista duplamente encadeada, busca binária e Insertion Sort. Aqui, a pessoa idosa tira a dúvida sozinha. Lá, a equipe de atendimento organiza os pedidos que precisam de ajuda presencial.

## Fontes consultadas

| Orientação | Fonte oficial |
|---|---|
| 1 Carteira da Pessoa Idosa · 11 Viagem interestadual | https://www.gov.br/pt-br/servicos/adquirir-carteira-do-idoso |
| 2 Atendimento prioritário (Estatuto da Pessoa Idosa) | https://www.planalto.gov.br/ccivil_03/leis/2003/l10.741.htm |
| 3 BPC para pessoa idosa | https://www.gov.br/pt-br/servicos/solicitar-beneficio-assistencial-ao-idoso |
| 4 Prova de vida · 13 Golpes | https://www.gov.br/inss/pt-br/assuntos/te-ligaram-ou-foram-a-sua-casa-dizendo-que-e-para-fazer-a-prova-de-vida-do-inss-cuidado-e-golpe |
| 5 Bloqueio para consignado | https://www.gov.br/inss/pt-br/centrais-de-conteudo/imagens/Passoapassodesbloqueiocomcontabancria.pdf |
| 6 Meu INSS e Central 135 | https://www.gov.br/inss/pt-br/e-fake-inss-nao-liga-da-central-135-para-pedir-dados-aos-cidadaos |
| 7 e 8 Farmácia Popular (remédios e fraldas) | https://www.gov.br/saude/pt-br/composicao/sectics/farmacia-popular |
| 9 Vacinação | https://www.gov.br/saude/pt-br/vacinacao |
| 10 Ônibus, metrô e trem em SP | https://atendimento.sptrans.com.br |
| 12 Disque 100 | https://www.gov.br/mdh/pt-br/ondh |

Todas as fontes foram conferidas pela equipe em 18/11/2026.

## Decisão técnica

Mantivemos a busca por regras e acrescentamos um **dicionário de sinônimos em JSON**, em vez de usar um modelo de IA:

- **Explicável:** o assistente mostra as palavras que levaram à resposta.
- **Previsível:** a mesma pergunta sempre dá o mesmo resultado.
- **Seguro:** num assistente sobre benefícios e golpes, uma resposta inventada pode fazer a pessoa perder dinheiro ou um direito.
- **Fácil de melhorar:** com os sinônimos fora do código, a equipe aumenta o vocabulário editando só o JSON.

## Limitações

- O assistente só conhece as 13 orientações da base. Outros assuntos recebem "não encontrei".
- Erros de digitação ("onibuz", "remedo") não são reconhecidos.
- O alerta de golpe é por regras e pode deixar passar golpes descritos com outras palavras.
- As regras de benefícios e transporte mudam. As orientações valem para a data de verificação e precisam ser revisadas.
- A orientação 10 vale para a cidade de São Paulo. Outras cidades da Grande SP têm regras próprias para os ônibus municipais.
- O assistente funciona só no terminal e exige digitação. Para muitas pessoas idosas, isso significa usar com a ajuda de um familiar ou atendente.
