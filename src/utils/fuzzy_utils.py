from thefuzz import fuzz

# Defeitos padrão (todos devem ser validados por nome)
DEFEITOS_PADRAO = [
    "oxidação", "trincado", "danificado", "não liga", 
    "não gera imagem", "em curto", "peça falsa/de terceiros", "empenado"
]

# Peças padrão
PECAS_PADRAO = [
    "tela", "tampa", "placa", "sub", "flex", "coaxial", 
    "bateria", "câmera frontal", "câmera traseira", "cabo"
]

def fuzzy_corresponde(nome, lista_padrao, limiar=70):

    # Retorna o item do padrao mais parecido com o nome dado
    # Usa múltiplas estratégias de matching para melhor precisão.

    nome_lower = nome.lower()
    melhor = None
    melhor_score = 0

    for item in lista_padrao:
        item_lower = item.lower()

        # Estratégia 1: Ratio completo
        score1 = fuzz.ratio(nome_lower, item_lower)

        # Estratégia 2: Partial ratio (melhor para quando o item esta dentro do nome)
        score2 = fuzz.partial_ratio(nome_lower, item_lower)

        # Estratégia 3: Token sort ratio (ignora ordem das palvras)
        score3 = fuzz.token_sort_ratio(nome_lower, item_lower)

        # Estratégia 4: Verifica se o item está contido no nome
        score4 = 100 if item_lower in nome_lower else 0

        # Usa o melhor score das estratégias
        score_final = max(score1, score2, score3, score4)

        if score_final > melhor_score:
            melhor_score = score_final
            melhor = item

    if melhor_score >= limiar:
        return melhor
    return None 

def defeito_corresponde(nome_arquivo):
    # Identifica se o nome do arquivo corresponde a algum defeito conhecido.
    # Usa limiar mais baixo pois defeitos podem ter variações.
 
    return fuzzy_corresponde(nome_arquivo, DEFEITOS_PADRAO, limiar=65)

def peca_corresponde(nome_arquivo):
    # Identifica se o nome do arquivo corresponde a alguma peça conhecida

    return fuzzy_corresponde(nome_arquivo, PECAS_PADRAO, limiar=70)

def extrair_numero_os(nome_arquivo):
    # Extrai o número da OS do nome do arquivo.
    # Assume que a OS é uma sequência de números no início do nome.

    import re
    match = re.match(r'^(\d+)', nome_arquivo)
    if match:
        return match.group(1)
    return None

def debug_matching(nome_arquivo):
    # Função para debug - mostra como orquivo está sendo interepretado
    print(f"\n DEBUG: Analisando '{nome_arquivo}'")

    defeito = defeito_corresponde(nome_arquivo)
    peca = peca_corresponde(nome_arquivo)
    os_num = extrair_numero_os(nome_arquivo)

    print(f" OS: {os_num or 'Não encontrada'}")
    print(f" Peça: {peca or 'Não identificada'}")
    print(f" Defeito {defeito or 'Não identificado'}")

    # Mostra scores detalhados para defeitos
    print(f" Scores defeitos:")
    for defeito_padrao in DEFEITOS_PADRAO:
        score = fuzz.partial_ratio(nome_arquivo.lower(), defeito_padrao.lower())
        if score > 50:
            print(f" {defeito_padrao}: {score}")

    # Mostra scores detalhados para peças
    print(f" Score peças:")
    for peca_padrao in PECAS_PADRAO:
        score = fuzz.partial_ratio(nome_arquivo.lower(), peca_padrao.lower)
        if score > 50:
            print(f" {peca_padrao}: {score}")

# Função para testar o sistema
def testar_exemplos():
    # Testa o sistema com exemplos reais
    exemplos = [
        "4173482829 placa não liga",
        "4173482829 tela trincado", 
        "4173482829 tampa danificado",
        "4173482829 flex em curto",
        "OS123456 bateria oxidação",
        "frente_tela_4173482829",
        "verso_tampa_4173482829",
        "lateral1_4173482829"
    ]

    print(f"🧪 TESTANDO EXEMPLOS: ")
    print("=" * 50)

    for exemplo in exemplos:
        debug_matching(exemplo)

if __name__ == "__main__":
    testar_exemplos()