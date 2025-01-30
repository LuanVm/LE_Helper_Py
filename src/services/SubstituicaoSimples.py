import os
from dataclasses import dataclass

@dataclass
class ResultadoRenomeacao:
    arquivos_alterados: int
    erros: list[str]

class SubstituicaoSimples:
    @staticmethod
    def renomear_arquivos(pasta: str, palavra_antiga: str, palavra_nova: str) -> ResultadoRenomeacao:
        erros = []
        arquivos_alterados = 0

        if not os.path.isdir(pasta):
            raise ValueError("Diretório inválido")

        for nome_arquivo in os.listdir(pasta):
            caminho_antigo = os.path.join(pasta, nome_arquivo)
            
            if os.path.isfile(caminho_antigo):
                novo_nome = nome_arquivo.replace(palavra_antiga, palavra_nova)
                if novo_nome != nome_arquivo:
                    try:
                        caminho_novo = os.path.join(pasta, novo_nome)
                        os.rename(caminho_antigo, caminho_novo)
                        arquivos_alterados += 1
                    except Exception as e:
                        erros.append(f"Erro ao renomear {nome_arquivo}: {str(e)}")

        return ResultadoRenomeacao(
            arquivos_alterados=arquivos_alterados,
            erros=erros
        )