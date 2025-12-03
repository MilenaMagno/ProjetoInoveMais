import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import data_manager
from Const import styles
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk

# Configuração de Imagem de Fundo
NOME_IMAGEM_FUNDO = "fundo_menu.png"
PASTA_IMAGEM = "imagens_menu"
CAMINHO_IMAGEM = os.path.join(PASTA_IMAGEM, NOME_IMAGEM_FUNDO)


def mostrar_resultados_em_nova_janela(titulo, texto):
    """Cria uma nova janela para exibir o texto de resultado"""

    janela_resultado = tk.Toplevel()
    janela_resultado.title(titulo)
    janela_resultado.geometry("800x600")

    lbl_titulo = tk.Label(janela_resultado,
                          text=titulo,
                          font=styles.FONTE_TITULO,
                          pady=10)
    lbl_titulo.pack(pady=10)

    # Campo de texto com barra de rolagem
    txt_resultados = scrolledtext.ScrolledText(janela_resultado,
                                               wrap=tk.WORD,
                                               font=styles.FONTE_RESULTADO,
                                               padx=10,
                                               pady=10)
    txt_resultados.insert(tk.INSERT, texto)
    txt_resultados.config(state=tk.DISABLED)
    txt_resultados.pack(expand=True, fill='both', padx=20, pady=10)

# Funções para os Botões

def consultar_porcentagens():
    """Função que chama a lógica de dados e exibe o resultado"""
    # Garante que os dados do DB estão atualizados
    data_manager.calcular_porcentagens_por_semestre()

    # Recupera o texto formatado para exibição
    resultados_db = data_manager.db.get_todos_resultados()

    if not resultados_db:
        messagebox.showerror("Erro de Consulta", "Nenhum dado de semestre encontrado ou processado.")
        return

    resultado_str = data_manager.formatar_resultados_para_exibicao(resultados_db)

    if resultado_str.startswith("Ocorreu um erro") or resultado_str.startswith("Nenhum dado"):
        messagebox.showerror("Erro de Consulta", resultado_str)
    else:
        mostrar_resultados_em_nova_janela("Consulta de Porcentagens por Semestre", resultado_str)


def ver_dados_alunos():
    """Função para o botão 'Dados de Alunos' - Abre a janela de consulta"""

    dados_alunos = data_manager.carregar_dados_alunos_individuais()

    if dados_alunos.empty:
        # Mensagem quando o arquivo opcional não é encontrado
        messagebox.showwarning("Dados Alunos",
                               "O arquivo opcional de dados individuais ('dados_alunos_individuais.xlsx') não foi encontrado ou está vazio na pasta 'Dados'. Por favor, crie o arquivo e tente novamente.")
    else:
        abrir_janela_dados_alunos(dados_alunos)


def abrir_janela_dados_alunos(df_alunos):
    """Cria a janela com campo de busca e exibe os dados"""

    janela_dados = tk.Toplevel()
    janela_dados.title("Consulta de Dados de Alunos Individuais")
    janela_dados.geometry("1000x700")

    lbl_titulo = tk.Label(janela_dados, text="Dados Individuais dos Alunos", font=styles.FONTE_TITULO, pady=10)
    lbl_titulo.pack(pady=10)

    # --- Área de Busca ---
    frame_busca = tk.Frame(janela_dados)
    frame_busca.pack(pady=10, padx=10)

    lbl_busca = tk.Label(frame_busca, text="Buscar Nome do Inscrito (ou parte):", font=styles.FONTE_BOTAO)
    lbl_busca.pack(side=tk.LEFT, padx=5)

    entrada_nome = tk.Entry(frame_busca, width=50, font=styles.FONTE_RESULTADO)
    entrada_nome.pack(side=tk.LEFT, padx=5)

    # Campo de texto para exibir resultados
    txt_resultados = scrolledtext.ScrolledText(janela_dados, wrap=tk.WORD, font=styles.FONTE_RESULTADO, padx=10,
                                               pady=10)
    txt_resultados.pack(expand=True, fill='both', padx=20, pady=10)

    def exibir_dados(df):
        """Formata e exibe o DataFrame no campo de resultados"""
        txt_resultados.config(state=tk.NORMAL)  # Habilita para escrita
        txt_resultados.delete(1.0, tk.END)
        if df.empty:
            txt_resultados.insert(tk.INSERT, "Nenhum resultado encontrado.")
        else:
            # Exibe o DataFrame como string, sem o índice
            dados_str = df.to_string(index=False)
            txt_resultados.insert(tk.INSERT, dados_str)
        txt_resultados.config(state=tk.DISABLED)  # Desabilita edição

    def buscar_nome():
        """Filtra os dados com base no nome digitado"""
        termo_busca = entrada_nome.get().strip().upper()

        if termo_busca:
            # Filtra onde 'nome_inscrito' contém o termo buscado
            df_filtrado = df_alunos[
                df_alunos['nome_inscrito'].str.contains(termo_busca, na=False)
            ]
        else:
            # Se a busca estiver vazia, exibe todos os dados
            df_filtrado = df_alunos

        exibir_dados(df_filtrado)

    btn_buscar = tk.Button(frame_busca,
                           text="Buscar",
                           command=buscar_nome,
                           bg=styles.BG_BOTAO_PADRAO,
                           fg=styles.FG_BOTAO,
                           font=styles.FONTE_BOTAO)
    btn_buscar.pack(side=tk.LEFT, padx=5)

    # Exibe todos os dados na abertura da janela
    exibir_dados(df_alunos)


def criar_dashboard():
    """Cria e exibe o dashboard de porcentagens em uma nova janela."""

    # Garante que os dados do DB estão atualizados
    data_manager.calcular_porcentagens_por_semestre()

    # Recupera os dados no formato adequado para o Matplotlib
    dados_dashboard = data_manager.get_resultados_dashboard()

    if not dados_dashboard:
        messagebox.showwarning("Dashboard",
                               "Nenhum dado de semestre encontrado para gerar o dashboard. Verifique o arquivo principal.")
        return

    # Preparação dos Dados
    # Ordena os semestres do mais antigo para o mais recente
    dados_dashboard.sort(key=lambda d: (int(d['semestre'].split('/')[1]), int(d['semestre'].split('/')[0])))

    semestres = [d['semestre'] for d in dados_dashboard]
    formados = [d['perc_formados'] for d in dados_dashboard]
    desistentes = [d['perc_desistentes'] for d in dados_dashboard]
    nunca_foram = [d['perc_nunca_foram'] for d in dados_dashboard]

    # Configuração da Janela e do Gráfico
    janela_dashboard = tk.Toplevel()
    janela_dashboard.title("Dashboard - Porcentagens por Semestre")
    janela_dashboard.geometry("1000x700")

    lbl_titulo = tk.Label(janela_dashboard,
                          text="Dashboard de Formação e Evasão por Semestre",
                          font=styles.FONTE_TITULO,
                          pady=10)
    lbl_titulo.pack(pady=10)

    # Cria a figura do Matplotlib
    fig = plt.Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    largura = 0.6  # Largura das barras

    # Criação do Gráfico de Barras Empilhadas

    # Base para as próximas barras (onde a barra começa)
    bottom_desistentes = np.array(formados)
    bottom_nunca_foram = np.array(formados) + np.array(desistentes)

    # Plota as barras
    ax.bar(semestres, formados, largura, label='Formados', color='#27ae60')  # Verde
    ax.bar(semestres, desistentes, largura, bottom=bottom_desistentes, label='Desistentes', color='#f39c12')  # Laranja
    ax.bar(semestres, nunca_foram, largura, bottom=bottom_nunca_foram, label='Nunca Foram', color='#e74c3c')  # Vermelho

    # Configurações Adicionais
    ax.set_ylabel('Porcentagem (%)', fontsize=12)
    ax.set_title('Distribuição dos Selecionados por Semestre', fontsize=14)

    # Rotação para Semestres longos
    ax.set_xticks(semestres)
    ax.tick_params(axis='x', rotation=45)

    ax.legend(loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.3))
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout()  # Ajusta automaticamente para evitar corte

    # Inserção do Matplotlib no Tkinter
    canvas = FigureCanvasTkAgg(fig, master=janela_dashboard)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    canvas.draw()

# Janela Principal

def criar_janela_menu():
    janela = tk.Tk()
    janela.title("Menu Principal - Gestão de Dados do Programa Inove Mais (EFG)")
    janela.geometry("600x400")
    janela.resizable(False, False)

    global imagem_fundo_tk

    try:
        # Tenta carregar a imagem usando PIL/Pillow
        img_pil = Image.open(CAMINHO_IMAGEM)
        imagem_fundo_tk = ImageTk.PhotoImage(img_pil)

        fundo = tk.Label(janela, image=imagem_fundo_tk)
        fundo.place(x=0, y=0, relwidth=1, relheight=1)

        titulo = tk.Label(janela,
                          text="MENU DE OPÇÕES",
                          font=styles.FONTE_TITULO,
                          bg=styles.BG_TITULO_FUNDO,
                          fg=styles.FG_TITULO)
        titulo.pack(pady=40)

    except Exception:
        # Captura qualquer erro e usa cor simples
        messagebox.showwarning("Erro de Imagem",
                               f"A imagem '{CAMINHO_IMAGEM}' não foi encontrada, formato inválido ou Pillow não está instalado. Usando cor de fundo simples.")
        janela.configure(bg=styles.BG_PRINCIPAL)

        titulo = tk.Label(janela,
                          text="MENU DE OPÇÕES",
                          font=styles.FONTE_TITULO,
                          bg=styles.BG_PRINCIPAL,
                          fg=styles.FG_TITULO)
        titulo.pack(pady=20)

    # Botão 1: Consultar Porcentagens
    tk.Button(janela,
              text="1. Consultar Porcentagens",
              command=consultar_porcentagens,
              **styles.ESTILO_BOTAO_PADRAO).pack(pady=15)

    # Botão 2: Consultar Dados de Alunos
    tk.Button(janela,
              text="2. Consultar dados de alunos",
              command=ver_dados_alunos,
              **styles.ESTILO_BOTAO_PADRAO).pack(pady=15)

    # Botão 3: Dashboard (NOVO)
    tk.Button(janela,
              text="3. Ver Dashboard Gráfico",
              command=criar_dashboard,
              **styles.ESTILO_BOTAO_PADRAO).pack(pady=15)

    janela.mainloop()


# Inicia o aplicativo
if __name__ == "__main__":
    # Garante que o banco de dados seja inicializado antes de tudo
    data_manager.db.init_db()
    criar_janela_menu()
