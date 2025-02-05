import re
from PyPDF2 import PdfReader

def extrair_contrato(caminho_pdf):
    """
    Extrai o número do contrato de um PDF. O contrato deve estar logo abaixo
    do valor da fatura e do rótulo "Contrato". O número pode ter de 2 a 7 dígitos,
    podendo vir com zeros à esquerda que serão removidos.
    """
    try:
        # Abre o arquivo em modo binário
        with open(caminho_pdf, "rb") as f:
            leitor = PdfReader(f)
            texto = "".join(pagina.extract_text() or "" for pagina in leitor.pages)
        
        # Novo padrão:
        # - Procura o rótulo "Contrato"
        # - Em seguida, o valor da fatura (ex: "R$ 59,90")
        # - Em seguida, o número do contrato, possivelmente com zeros à esquerda.
        padrao = re.compile(
            r'Contrato\s*R\$\s*\d{1,4}(?:[.,]\d{3})*[.,]\d{2}\s*0*(\d{1,7})',
            re.IGNORECASE
        )
        match = padrao.search(texto)
        if match:
            # Remove os zeros à esquerda convertendo para int e de volta para str.
            contrato_sem_zero = str(int(match.group(1)))
            return contrato_sem_zero

        return None
    except Exception as erro:
        print(f"Erro: {erro}")
        return None

def testar_com_pdf(caminho_pdf):
    contrato = extrair_contrato(caminho_pdf)
    if contrato:
        print(f"Contrato identificado: {contrato}")
    else:
        print("Contrato não encontrado, movendo arquivo.")

if __name__ == '__main__':
    print("Teste com PDF real:")
    caminho_pdf = r"C:\Users\LUANVITOR\OneDrive - Welington Henrique Baggio\Área de Trabalho\Geral\testes\coleta_blume\ete.pdf"
    testar_com_pdf(caminho_pdf)

    #"C:\Users\LUANVITOR\Downloads\f488fe3b89f63b8a3539790a377c5b55.pdf"
    #"C:\Users\LUANVITOR\OneDrive - Welington Henrique Baggio\Área de Trabalho\Geral\testes\coleta_blume\test2.pdf"