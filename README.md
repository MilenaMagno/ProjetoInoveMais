# 📊 Projeto Inove Mais: Gestão de Dados e Dashboard Acadêmico

## Descrição do Projeto

Ferramenta de gestão de dados acadêmicos desenvolvida em **Python** com interface gráfica (GUI) utilizando **Tkinter** e visualização de dados com a biblioteca **Matplotlib**.

Ele foi criado para processar resultados de planilhas (`.xlsx`) de semestres e calcular métricas cruciais de desempenho e evasão. O principal objetivo é fornecer uma visão clara
e objetiva sobre a evolução da porcentagem de alunos formados, desistentes e aqueles que nunca iniciaram o programa ao longo do tempo.

## ✨ Principais Funcionalidades

* **Processamento de Dados:** Leitura de múltiplas abas de um arquivo principal (`dados_inove_mais.xlsx`) para consolidar resultados.
* **Cálculo de Porcentagens:** Determinação da taxa de Formados, Desistentes (1 a 3 presenças) e Evasão (0 presenças) por semestre.
* **Dashboard Gráfico:** Visualização das porcentagens de Formação, Desistência e Evasão em um gráfico de barras empilhadas para uma análise comparativa clara.
* **Consulta:** Permite a busca e visualização de dados de alunos específicos (utilizando arquivo auxiliar).
* **Banco de Dados SQLite:** Utilizado para inicializar e armazenar os resultados consolidados (`dados_academicos.db`) para acesso rápido.
  
## Estrutura de pastas

  ProjetoInoveMais/
├── Const/
│   └── styles.py                 # Arquivo com definições de estilo (cores, fontes, etc.)
├── Dados/
│   ├── dados_inove_mais.xlsx     # Arquivo principal (com abas de resultados)
│   └── dados_alunos_individuais.xlsx # Arquivo opcional para consulta individual
├── imagens_menu/
│   └── fundo_menu.png            # Imagem de fundo do menu principal
├── main_app.py                   # Arquivo principal (ponto de entrada da GUI)
├── data_manager.py               # Lógica de processamento de dados e cálculos
└── database.py                   # Funções de interação com o SQLite


## Instalação das Bibliotecas

Abra o terminal na raiz do projeto e execute:
pip install pandas matplotlib numpy Pillow openpyxl

## 📦 Empacotamento (Arquivo .EXE)

O projeto foi empacotado para distribuição em Windows usando PyInstaller. O executável (main_app.exe) foi gerado na pasta /dist.
Para rodar o aplicativo final, você deve copiar o arquivo main_app.exe junto com as pastas Dados e imagens_menu para um mesmo local.

Desenvolvido por: Milena Magno.
