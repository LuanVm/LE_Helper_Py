import re
from PyPDF2 import PdfReader

def extract_cnpjs_from_pdf(file_path):
    """
    Função para extrair CNPJs de um arquivo PDF utilizando PyPDF2.
    
    Returns:
        list: Lista de CNPJs encontrados no PDF.
    """
    cnpjs = []
    try:
        # Abrir o PDF e ler o texto
        reader = PdfReader(file_path)
        for page in reader.pages:
            # Extrair o texto da página
            text = page.extract_text()
            if text:
                # Buscar CNPJs no texto utilizando regex
                matches = re.findall(r"\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}", text)
                cnpjs.extend(matches)
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
    
    return cnpjs

if __name__ == "__main__":
    file_path = r"C:\Users\LUANVITOR\OneDrive - Welington Henrique Baggio\Área de Trabalho\Geral\testes\Notas Fiscais Metropolitano\PA-01.pdf"
    
    cnpjs_encontrados = extract_cnpjs_from_pdf(file_path)
    
    if cnpjs_encontrados:
        print("CNPJs encontrados:")
        for idx, cnpj in enumerate(cnpjs_encontrados, start=1):
            print(f"{idx}: {cnpj}")
        
        # Selecionar o segundo CNPJ (índice 1, pois trata-se do CNPJ esperado)
        # Verifique se há pelo menos dois CNPJs
        if len(cnpjs_encontrados) > 1:
            segundo_cnpj = cnpjs_encontrados[1]
            print(f"\nSegundo CNPJ identificado: {segundo_cnpj}")
        else:
            print("\nMenos de dois CNPJs encontrados no arquivo.")
    else:
        print("Nenhum CNPJ encontrado no arquivo.")
