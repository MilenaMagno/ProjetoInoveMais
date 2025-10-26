import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import data_manager
from Const import styles

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
    resultado_str = data_manager.consultar_porcentagens()

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


# Janela Principal
def criar_janela_menu():
    janela = tk.Tk()
    janela.title("Menu Principal - Gestão de Dados do Programa Inove Mais (EFG)")
    janela.geometry("600x400")
    janela.resizable(False, False)

    global imagem_fundo_tk

    try:
        imagem_original = tk.PhotoImage(file=CAMINHO_IMAGEM)
        imagem_fundo_tk = imagem_original

        fundo = tk.Label(janela, image=imagem_fundo_tk)
        fundo.place(x=0, y=0, relwidth=1, relheight=1)

        titulo = tk.Label(janela,
                          text="MENU DE OPÇÕES",
                          font=styles.FONTE_TITULO,
                          bg=styles.BG_TITULO_FUNDO,
                          fg=styles.FG_TITULO)
        titulo.pack(pady=40)

    except tk.TclError:
        messagebox.showwarning("Erro de Imagem",
                               f"A imagem '{CAMINHO_IMAGEM}' não foi encontrada ou o formato é inválido. Usando cor de fundo simples.")
        janela.configure(bg=styles.BG_PRINCIPAL)

        titulo = tk.Label(janela,
                          text="MENU DE OPÇÕES",
                          font=styles.FONTE_TITULO,
                          bg=styles.BG_PRINCIPAL,
                          fg=styles.FG_TITULO)
        titulo.pack(pady=20)

    # Botão 1: Consultar Porcentagens
    estilo_botao_consulta = styles.ESTILO_BOTAO_PADRAO.copy()
    estilo_botao_consulta['bg'] = styles.BG_BOTAO_DESTAQUE

    tk.Button(janela,
              text="1. Consultar Porcentagens",
              command=consultar_porcentagens,
              **styles.ESTILO_BOTAO_PADRAO).pack(pady=15)

    # Botão 2: Consultar Dados de Alunos
    tk.Button(janela,
              text="2. Consultar dados de alunos",
              command=ver_dados_alunos,
              **styles.ESTILO_BOTAO_PADRAO).pack(pady=15)

    janela.mainloop()


# Inicia o aplicativo
if __name__ == "__main__":
    criar_janela_menu()
