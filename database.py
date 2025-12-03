import sqlite3

DB_NAME = "dados_academicos.db"


def init_db():
    """Inicializa o banco de dados e cria a tabela de resultados se ela não existir"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Cria a tabela para armazenar os resultados dos cálculos por semestre
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS resultados_semestre
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           semestre
                           TEXT
                           NOT
                           NULL
                           UNIQUE,
                           perc_formados
                           REAL,
                           nomes_formados
                           TEXT,
                           perc_desistentes
                           REAL,
                           nomes_desistentes
                           TEXT,
                           perc_nunca_foram
                           REAL,
                           nomes_nunca_foram
                           TEXT,
                           perc_multisemestre
                           REAL,
                           nomes_multisemestre
                           TEXT
                       );
                       """)
        conn.commit()
        conn.close()
        print("Banco de dados inicializado com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")


def salvar_resultado_semestre(dados_semestre):
    """Salva ou atualiza os resultados de um semestre específico no banco de dados"""

    # Garante que todos os campos de nomes sejam strings
    nomes_formados_str = ", ".join(dados_semestre['nomes_formados'])
    nomes_desistentes_str = ", ".join(dados_semestre['nomes_desistentes'])
    nomes_nunca_foram_str = ", ".join(dados_semestre['nomes_nunca_foram'])
    # Usa .get() para garantir que não quebre se for o primeiro semestre e não tiver multi
    nomes_multisemestre_str = ", ".join(dados_semestre.get('nomes_multisemestre', []))

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # SQL para inserir ou atualizar
        sql = """
        INSERT OR REPLACE INTO resultados_semestre 
        (semestre, perc_formados, nomes_formados, perc_desistentes, nomes_desistentes, perc_nunca_foram, nomes_nunca_foram, perc_multisemestre, nomes_multisemestre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(sql, (
            dados_semestre['semestre'],
            dados_semestre['perc_formados'],
            nomes_formados_str,
            dados_semestre['perc_desistentes'],
            nomes_desistentes_str,
            dados_semestre['perc_nunca_foram'],
            nomes_nunca_foram_str,
            dados_semestre.get('perc_multisemestre', 0.0),
            nomes_multisemestre_str
        ))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Erro ao salvar dados do {dados_semestre['semestre']}: {e}")


def get_todos_resultados():
    """Retorna todos os resultados de todos os semestres salvos no DB"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM resultados_semestre ORDER BY semestre DESC")
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    except sqlite3.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return []


def get_dados_resultados():
    """Retorna todos os resultados de todos os dados salvos no DB"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Ordena por semestre de forma descendente
        # ALTERADO para ordenar as COLUNAS (no SELECT) e as LINHAS (no ORDER BY)
        resultado_dados = cursor.execute(
            "SELECT nome_inscrito, telefone, \"e-mail\", endereco, proposta_de_projeto, semestre FROM resultados_semestre ORDER BY nome_inscrito ASC").fetchall()

        conn.close()
        return resultado_dados

    except sqlite3.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return []


# Inicializa o DB ao importar o arquivo
init_db()
