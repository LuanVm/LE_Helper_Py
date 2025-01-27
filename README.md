# LE Helper

**LE Helper** é um aplicativo baseado em **PyQt6**, criado para facilitar tarefas automatizadas, como organização de arquivos, mesclagem de planilhas, automação de coleta de dados e substituições simples. O software visa melhorar a eficiência em processos repetitivos e proporcionar uma interface amigável para os usuários.

---

## Funcionalidades Principais

### 1. Interface Principal
- Utiliza o **PyQt6** para criar uma interface rica e responsiva.
- **Design adaptável**: Inclui gerenciador de temas (“light” e “dark”).
- **Barra de título personalizada**, com botões para minimizar e fechar o aplicativo.

### 2. Painel de Automação da Coleta
- Automatiza a coleta de faturas via web scraping utilizando **Selenium** e **webdriver_manager**.
- Inclui funcionalidade de login automático em portais.
- Realiza downloads e processa PDFs para extrair informações específicas.
- Atualiza uma planilha Excel com o status das faturas coletadas.

### 3. Painel de Organização de Pastas
- Organiza arquivos automaticamente em subpastas com base em padrões configuráveis.
- Possui recurso de edição da lista de clientes/padrões para personalização.
- Permite buscar arquivos em subpastas e consolidá-los em um diretório único.

### 4. Painel de Processamento de Planilhas
- **Mesclagem de Planilhas**: Permite consolidar vários arquivos Excel em um único arquivo.
- Suporta seleção personalizada de colunas e aplica estilos baseados em um arquivo de referência.
- Inclui barra de progresso e logs detalhados para monitoramento do processo.

### 5. Painel de Substituição Simples
- Executa substituições em arquivos de texto com base em padrões predefinidos.

### 6. Tela Inicial (Home)
- Oferece um menu interativo para navegar entre as diferentes funções.
- Inclui animações suaves para elementos visuais.

---

## Tecnologias Utilizadas

- **Python 3.9+**
- **PyQt6**: Criação da interface gráfica.
- **Selenium**: Para automação de navegador.
- **OpenPyXL**: Manipulação de arquivos Excel.
- **PyPDF2**: Extração de texto de PDFs.
- **webdriver_manager**: Gerenciamento automático de drivers para navegadores.

---

## Estrutura do Projeto

### Diretórios Principais:
- **/modules**: Contém os diferentes paineis do aplicativo.
- **/utils**: Inclui utilitários e funções auxiliares, como gerenciamento de temas e estilos.
- **/resources**: Armazena ícones e outros recursos visuais.

### Arquivo Principal:
- `allcode.py`: Contém o código principal que inicializa e configura o aplicativo.

---

## Instalação e Execução

### Requisitos:
- **Python 3.9 ou superior**
- **Gerenciador de pacotes**: `pip`

### Instalação dos Pacotes Necessários:
```bash
pip install PyQt6 selenium openpyxl pypdf2 webdriver_manager
```

### Como Executar:
1. Clone este repositório ou baixe os arquivos.
2. Navegue até o diretório do projeto.
3. Execute o arquivo principal:
   ```python src/main.py```
