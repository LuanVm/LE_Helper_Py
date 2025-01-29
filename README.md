# LE Helper

**LE Helper** é um aplicativo baseado em **PyQt6**, criado para facilitar tarefas automatizadas, como organização de arquivos, mesclagem de planilhas, automação de coleta de dados e substituições simples. O software visa melhorar a eficiência em processos repetitivos e proporcionar uma interface amigável para os usuários.

---

## Funcionalidades Principais
### 1. Interface Principal
- Utiliza o **PyQt6** para criar uma interface rica e responsiva.
- **Design adaptável**, possui gerenciador de temas (“light” e “dark”).
- **Barra de título personalizada**, com botões para minimizar e fechar o aplicativo.

### 2. Painel de Automação para Coleta de Faturas
- Automatiza a coleta de faturas via web scraping utilizando **Selenium** e **webdriver_manager**.
- Inclui funcionalidade de login automático em portais.
- Realiza downloads e processa PDFs para extrair informações específicas.
- Atualiza uma planilha Excel com o status das faturas coletadas.

### 3. Painel de Organização de Pastas
- Organiza arquivos automaticamente em subpastas com base em padrões configuráveis, considerando a lista do botão "Editar clientes", que utiliza os dados armazenados no arquivo ```clientes.properties.```
- Permite buscar arquivos em subpastas e consolidá-los em um diretório único, realizando a remoção das pastas vazias após a movimentação de arquivos para o diretório raiz.
- Possui recurso de edição da lista de clientes/padrões para personalização.

### 4. Painel de Processamento de Planilhas
- **Mesclagem de Planilhas**, permite consolidar vários arquivos Excel em um único arquivo.
- Suporta seleção personalizada de colunas e aplica estilos baseados em um arquivo de referência.
- Inclui barra de progresso e logs detalhados para monitoramento do processo.

### 5. Painel de Substituição Simples
- Executa substituições em arquivos de texto com base em padrões predefinidos, funcionando de maneira **semelhante ao CTRL + L ou F (Substituir)**, porém aplicado a uma pasta específica. Permite a alteração em qualquer tipo de arquivo que siga um padrão de nomenclatura, como, por exemplo, "Arquivo_1_Janeiro" e "Arquivo_2_Janeiro", possibilitando a seleção da palavra "Janeiro" e sua substituição por "Fevereiro" automaticamente.

### 6. Tela Inicial (Home)
- Oferece um menu interativo para navegar entre as diferentes funções.
- Inclui animações suaves para elementos visuais.
- Botões com cores aleatórias, redefinidas a cada inicialização com base em uma paleta de cores predefinida.

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

- **/services**: Contém a lógica de processamento (business).
- **/modules**: Contém os diferentes painéis do aplicativo.
- **/utils**: Inclui utilitários e funções auxiliares, como gerenciamento de temas e estilos.
- **/resources**: Armazena ícones e outros recursos visuais.

---

## Instalação e Execução
### Requisitos:
- **Python 3.9 ou superior**
- **Gerenciador de pacotes: pip**

### Instalação dos Pacotes Necessários:
```
bash
pip install PyQt6 selenium openpyxl pypdf2 webdriver_manager
```

### Como Executar:
1. Clone este repositório ou baixe os arquivos.
2. Navegue até o diretório do projeto.
3. Execute o arquivo principal:
```
bash
python src/main.py
```

---

### Benefícios para a Empresa
O LE Helper foi desenvolvido com base nas necessidades diárias da empresa Livre Escolha Assessoria. Com sua implementação, foi possível conquistar uma economia de aproximadamente 120 horas mensais nos setores da empresa, otimizando processos repetitivos e aumentando a produtividade.

### Novas Funcionalidades
- **Painel de Coleta**: Realiza a coleta de operadores e provedores de forma automatizada utilizando Selenium. Atualmente, a coleta é feita apenas na plataforma do provedor BLUME, mas o sistema é escalável para outras plataformas.

### Contribuições
**Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests para melhorar o projeto.**
