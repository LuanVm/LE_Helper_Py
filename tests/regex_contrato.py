import re
from PyPDF2 import PdfReader

def extrair_contrato(texto):
    """
    Extrai o número do contrato de uma string.
    
    Primeiro, tenta encontrar uma sequência que comece com três ou mais zeros seguidos de três ou mais dígitos.
    Se não encontrar, e se o texto contiver a palavra "Contrato", procura uma sequência de três ou mais dígitos
    logo após essa palavra.
    """
    # Primeira tentativa: busca padrão com zeros à esquerda.
    match = re.search(r'\b0{3,}(\d{3,})\b', texto)
    if match:
        return match.group(1)
    
    # Se não encontrou, verifica se há a palavra "Contrato" (case insensitive).
    if "contrato" in texto.lower():
        # Extrai o texto a partir da primeira ocorrência de "Contrato"
        indice = texto.lower().find("contrato")
        subtexto = texto[indice:]
        # Segunda tentativa: busca uma sequência de três ou mais dígitos no subtexto.
        match = re.search(r'(\d{3,})\b', subtexto)
        if match:
            return match.group(1)
    
    return None

def testar_regex():
    casos_de_teste = [
        ("O contrato é 000123456 e deve ser processado.", "123456"),
        ("Nenhum contrato aqui", None),
        ("Contratos: 000987, 000112233.", "987"),  # A regex encontra o primeiro match
        ("000555", "555"),
        ("Valor: 0000123", "123"),
        ("Contrato simples: 123456", "123456"),  # Agora o segundo padrão é aplicado
        ("Dados: Sem indicação de contrato.", None)
    ]

    for texto, esperado in casos_de_teste:
        resultado = extrair_contrato(texto)
        print(f"Texto: {texto}")
        print(f"Resultado: {resultado} (Esperado: {esperado})")
        print("-" * 40)

def testar_com_pdf(caminho_pdf):
    try:
        leitor = PdfReader(caminho_pdf)
        # Concatena o texto de todas as páginas do PDF
        texto_pdf = ""
        for pagina in leitor.pages:
            t = pagina.extract_text()
            if t:
                texto_pdf += t
        contrato = extrair_contrato(texto_pdf)
        print(f"Contrato extraído do PDF: {contrato}")
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")

if __name__ == '__main__':
    print("Teste com casos de exemplo:")
    testar_regex()
    print("\nTeste com PDF real:")
    caminho_pdf = r"C:\Users\LUANVITOR\OneDrive - Welington Henrique Baggio\Área de Trabalho\Geral\testes\coleta_blume\test.pdf"
    testar_com_pdf(caminho_pdf)
