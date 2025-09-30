import os
import sys
from utils.fuzzy_utils import defeito_corresponde, peca_corresponde

# Padrões de fotos por tipo de laudo
PADROES = {
    "tela_tampa": [
        "frente da tela", "verso da tela", "tampa", "serial", 
        "lateral1", "lateral2", "lateral3", "lateral4",
        "peça com defeito",  # usar fotos já enviadas
        "defeito"            # nome do arquivo renomeado indicando o defeito
    ],
    "placa_sub": [
        "frente da tela", "verso da tela", "tampa", "serial",
        "lateral1", "lateral2", "lateral3", "lateral4",
        "placa ou sub frente", "placa ou sub verso", 
        "defeito"  # foto do defeito com nome do arquivo renomeado
    ],
    "cam_bateria_flex_coaxial": [
        "frente da tela", "verso da tela", "tampa", "serial",
        "lateral1", "lateral2", "lateral3", "lateral4",
        "peça com defeito frente", "peça com defeito verso",  # nome do arquivo renomeado (frente/verso)
        "defeito"  # nome do arquivo renomeado indicando o defeito
    ],
    "terceiros": [
        "frente da tela", "verso da tela", "tampa", "serial",
        "lateral1", "lateral2", "lateral3", "lateral4",
        "frente da peça falsa", "verso da peça falsa", "evidência que peça é falsa",
        "frente da peça original", "verso da peça original", "evidência de originalidade"
    ]
}

def identificar_laudo(nome_pasta):
    """Identifica o tipo de laudo baseado no nome da pasta"""
    nome_lower = nome_pasta.lower()

    # Verifica terceiros primeiro (mais específico)
    if any(palavra in nome_lower for palavra in ["terceiro", "falsa", "original"]):
        return "terceiros"
    
    # Verifica placa e sub
    elif any(palavra in nome_lower for palavra in ["placa", "sub"]):
        return "placa_sub"
    
    # Verifica câmera, bateria, flex, coaxial
    elif any(palavra in nome_lower for palavra in ["cam", "câmera", "camera", "bateria", "flex", "coaxial"]):
        return "cam_bateria_flex_coaxial"
    
    # Default: Tela e tampa
    else:
        return "tela_tampa"

def extrair_info_nome_arquivo(nome_arquivo):
    """Extrai informações do nome do arquivo"""
    nome_sem_ext = os.path.splitext(nome_arquivo)[0]

    # Tenta identificar peça e defeito
    peca = peca_corresponde(nome_sem_ext)
    defeito = defeito_corresponde(nome_sem_ext)

    return {
        'nome_completo': nome_arquivo,
        'nome_sem_ext': nome_sem_ext,
        'peca': peca,
        'defeito': defeito,
        'eh_imagem': nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
    }

def mapear_arquivo_para_padrao(info_arquivo, padroes_laudo):
    """Mapeia um arquivo para os padrões necessários do laudo"""
    correspondencias = []
    nome_lower = info_arquivo['nome_sem_ext'].lower()

    for padrao in padroes_laudo:
        padrao_lower = padrao.lower()

        # === FOTOS PADRÃO (TODAS AS CATEGORIAS) ===
        if "frente da tela" in padrao_lower and "tela" in nome_lower and ("frente" in nome_lower or "front" in nome_lower):
            correspondencias.append(padrao)
        elif "verso da tela" in padrao_lower and "tela" in nome_lower and ("verso" in nome_lower or "back" in nome_lower):
            correspondencias.append(padrao)
        elif "tampa" in padrao_lower and "tampa" in nome_lower:
            correspondencias.append(padrao)
        elif "serial" in padrao_lower and "serial" in nome_lower:
            correspondencias.append(padrao)
        elif "lateral" in padrao_lower and "lateral" in nome_lower:
            # Verifica laterais específicas (lateral1, lateral2, etc)
            if padrao_lower in nome_lower:
                correspondencias.append(padrao)

        # === TELA E TAMPA ===
        elif "peça com defeito" in padrao_lower and padrao_lower == "peça com defeito":
            # Para tela/tampa, usa fotos já enviadas - verifica se tem peça identificada
            if info_arquivo['peca'] and info_arquivo['peca'].lower() in ['tela', 'tampa']:
                correspondencias.append(padrao)

        # === PLACA E SUB ===
        elif "placa ou sub frente" in padrao_lower:
            if info_arquivo['peca'] and info_arquivo['peca'].lower() in ['placa', 'sub'] and "frente" in nome_lower:
                correspondencias.append(padrao)
        elif "placa ou sub verso" in padrao_lower:
            if info_arquivo['peca'] and info_arquivo['peca'].lower() in ['placa', 'sub'] and "verso" in nome_lower:
                correspondencias.append(padrao)

        # === CÂMERA, BATERIA, FLEX, COAXIAL ===
        elif "peça com defeito frente" in padrao_lower:
            if (info_arquivo['peca'] and 
                any(p in info_arquivo['peca'].lower() for p in ['câmera', 'camera', 'bateria', 'flex', 'coaxial', 'cabo']) and
                "frente" in nome_lower):
                correspondencias.append(padrao)
        elif "peça com defeito verso" in padrao_lower:
            if (info_arquivo['peca'] and 
                any(p in info_arquivo['peca'].lower() for p in ['câmera', 'camera', 'bateria', 'flex', 'coaxial', 'cabo']) and
                "verso" in nome_lower):
                correspondencias.append(padrao)

        # === TERCEIROS ===
        elif "frente da peça falsa" in padrao_lower and "falsa" in nome_lower and "frente" in nome_lower:
            correspondencias.append(padrao)
        elif "verso da peça falsa" in padrao_lower and "falsa" in nome_lower and "verso" in nome_lower:
            correspondencias.append(padrao)
        elif "evidência que peça é falsa" in padrao_lower and ("evidencia" in nome_lower or "evidência" in nome_lower) and "falsa" in nome_lower:
            correspondencias.append(padrao)
        elif "frente da peça original" in padrao_lower and "original" in nome_lower and "frente" in nome_lower:
            correspondencias.append(padrao)
        elif "verso da peça original" in padrao_lower and "original" in nome_lower and "verso" in nome_lower:
            correspondencias.append(padrao)
        elif "evidência de originalidade" in padrao_lower and ("evidencia" in nome_lower or "evidência" in nome_lower) and "original" in nome_lower:
            correspondencias.append(padrao)

        # === DEFEITOS (TODAS AS CATEGORIAS) ===
        elif padrao_lower == "defeito" and info_arquivo['defeito']:
            # Arquivo renomeado indicando o defeito
            correspondencias.append(padrao)

    return correspondencias

def verificar_fotos(pasta):
    """Função principal de verificação"""
    print(f"\n🔍 Verificando pasta: {pasta}")

    if not os.path.exists(pasta):
        print("❌ Pasta não encontrada!")
        return
    
    # Identifica tipo de laudo
    laudo = identificar_laudo(os.path.basename(pasta))
    padroes_necessarios = PADROES[laudo]

    print(f"📋 Tipo de laudo: {laudo}")
    print(f"📸 Padrões necessários: {len(padroes_necessarios)}")

    # Lista arquivos na pasta
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    print(f"📁 Arquivos encontrados: {len(arquivos)}")

    # Analisa cada arquivo
    fotos_presentes = {padrao: False for padrao in padroes_necessarios}

    print(f"\n{'='*50}")
    print("📋 ANALISANDO ARQUIVOS:")
    print(f"{'='*50}")

    for arquivo in arquivos:
        info = extrair_info_nome_arquivo(arquivo)

        print(f"\n📄 {arquivo}")
        print(f"   Peça: {info['peca'] or 'Não identificada'}")
        print(f"   Defeito: {info['defeito'] or 'Não identificado'}")

        # Mapeia arquivo para padrões
        correspondencias = mapear_arquivo_para_padrao(info, padroes_necessarios)

        if correspondencias:
            for padrao in correspondencias:
                fotos_presentes[padrao] = True
                print(f"   ✅ Corresponde a: {padrao}")
        else:
            print(f"   ⚠️  Não corresponde a nenhum padrão necessário")

    # Relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL:")
    print(f"{'='*60}")

    # Separa fotos encontradas e faltantes
    encontradas = []
    faltando = []

    for padrao in padroes_necessarios:
        if fotos_presentes[padrao]:
            encontradas.append(padrao)
        else:
            faltando.append(padrao)

    # Mostra fotos encontradas
    if encontradas:
        print(f"\n✅ FOTOS ENCONTRADAS ({len(encontradas)}):")
        for foto in encontradas:
            print(f"   ✅ {foto}")

    # Mostra fotos faltantes
    if faltando:
        print(f"\n❌ FOTOS FALTANDO ({len(faltando)}):")
        for foto in faltando:
            print(f"   ❌ {foto}")

    # Resumo final
    total = len(padroes_necessarios)
    presentes = len(encontradas)

    print(f"\n📈 RESUMO:")
    print(f"   Total necessário: {total}")
    print(f"   Fotos presentes: {presentes}")
    print(f"   Fotos faltando: {len(faltando)}")

    if len(faltando) == 0:
        print(f"\n🎉 PARABÉNS! TODAS AS FOTOS ESTÃO PRESENTES!")
    else:
        print(f"\n⚠️  ATENÇÃO: {len(faltando)} foto(s) ainda precisam ser adicionadas!")

def main():
    if len(sys.argv) != 2:
        print("Uso: python verificar.py <pasta>")
        return
    
    pasta = sys.argv[1]
    verificar_fotos(pasta)

if __name__ == "__main__":
    main()