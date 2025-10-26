import pandas as pd
import os
import re
from collections import defaultdict
import database as db
import tkinter as tk
from tkinter import messagebox

PASTA_DADOS = "Dados"

# Configurações de Arquivos
NOME_ARQUIVO_PRINCIPAL = "Dados_inove_mais.xlsx" # Dividido por abas no formato: conteúdo_semestreAno
CAMINHO_ARQUIVO_PRINCIPAL = os.path.join(PASTA_DADOS, NOME_ARQUIVO_PRINCIPAL)

# Planilha de dados individuais (o código ignora se faltar)
NOME_ARQUIVO_ALUNOS = "dados_alunos_individuais.xlsx"
CAMINHO_ARQUIVO_ALUNOS = os.path.join(PASTA_DADOS, NOME_ARQUIVO_ALUNOS)


def _carregar_abas():
    """Lê todas as abas do arquivo Excel único e retorna um dicionário de DataFrames"""

    if not os.path.exists(CAMINHO_ARQUIVO_PRINCIPAL):
        messagebox.showerror("Erro de Dados",
                             f"ERRO: O arquivo principal '{NOME_ARQUIVO_PRINCIPAL}' não foi encontrado em '{PASTA_DADOS}'.")
        return {}

    try:
        xls = pd.ExcelFile(CAMINHO_ARQUIVO_PRINCIPAL)
        dfs = pd.read_excel(xls, sheet_name=None)

        # Limpa o cabeçalho de todos os DataFrames carregados
        for sheet_name, df in dfs.items():

            # Garante que a coluna seja uma string antes de tentar usar .lower()
            novas_colunas = []
            for col in df.columns:
                novas_colunas.append(str(col).lower().strip().replace(' ', '_'))

            df.columns = novas_colunas

            if 'nome_inscrito' not in df.columns:
                if not df.empty and len(df.columns) > 0:
                    # Tenta renomear a primeira coluna se 'nome_inscrito' não for encontrada
                    df.rename(columns={df.columns[0]: 'nome_inscrito'}, inplace=True)

            if 'nome_inscrito' in df.columns:
                # Padroniza nomes para facilitar a comparação
                df['nome_inscrito'] = df['nome_inscrito'].astype(str).str.strip().str.upper()

            dfs[sheet_name] = df

        return dfs

    except Exception as e:
        messagebox.showerror("Erro de Leitura", f"Erro ao carregar o arquivo {NOME_ARQUIVO_PRINCIPAL}: {e}")
        return {}


def carregar_dados_alunos_individuais():
    """Lê a planilha adicional de dados individuais dos alunos"""

    if not os.path.exists(CAMINHO_ARQUIVO_ALUNOS):
        # Retorna DataFrame vazio se o arquivo não existir
        return pd.DataFrame()

    try:
        df = pd.read_excel(CAMINHO_ARQUIVO_ALUNOS)
        # Limpa e padroniza o cabeçalho
        df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]

        # Garante que o nome do aluno está padronizado para junções futuras e busca
        if 'nome_inscrito' in df.columns:
            df['nome_inscrito'] = df['nome_inscrito'].astype(str).str.strip().str.upper()

        return df

    except Exception as e:
        print(f"Erro ao carregar o arquivo de alunos individuais: {e}")
        return pd.DataFrame()  # Retorna vazio em caso de erro de leitura


def calcular_porcentagens_por_semestre():
    """
    Coordena a leitura de todas as abas e o cálculo das porcentagens
    para cada semestre, salvando os resultados no DB
    """

    dfs_abas = _carregar_abas()

    if not dfs_abas:
        return {}

    dados_por_semestre = defaultdict(
        lambda: {'inscritos': None, 'selecionados': None, 'frequencia': None, 'formados': None})
    regex_semestre = r"(\d{2}\d{4})"

    # Organiza os DataFrames por tipo e semestre
    for nome_aba, df in dfs_abas.items():
        nome_aba_lower = nome_aba.lower()
        match = re.search(regex_semestre, nome_aba_lower)

        if match:
            semestre_raw = match.group(1)
            semestre_formatado = f"{semestre_raw[:2]}/{semestre_raw[2:]}"

            if 'inscritos_' in nome_aba_lower:
                dados_por_semestre[semestre_formatado]['inscritos'] = df
            elif 'selecionados_' in nome_aba_lower:
                dados_por_semestre[semestre_formatado]['selecionados'] = df
            elif 'frequencia_' in nome_aba_lower:
                dados_por_semestre[semestre_formatado]['frequencia'] = df
            elif 'formados_' in nome_aba_lower:
                dados_por_semestre[semestre_formatado]['formados'] = df

    todos_semestres = set(dados_por_semestre.keys())
    resultados_finais = {}

    # Cálculo reinscritos
    todos_inscritos_dict = defaultdict(list)
    for semestre, dados in dados_por_semestre.items():
        df_inscritos = dados.get('inscritos')
        if df_inscritos is not None and not df_inscritos.empty:
            for nome in df_inscritos.get('nome_inscrito', []):
                todos_inscritos_dict[nome].append(semestre)

    nomes_multi = [nome for nome, semestres in todos_inscritos_dict.items() if len(semestres) > 1]
    total_inscritos_unicos = len(todos_inscritos_dict)
    perc_multisemestre = (len(nomes_multi) / total_inscritos_unicos) * 100 if total_inscritos_unicos > 0 else 0.0

    # Processamento por Semestre
    for semestre in sorted(list(todos_semestres)):

        dados = dados_por_semestre[semestre]
        df_selecionados = dados.get('selecionados')

        if df_selecionados is None or df_selecionados.empty:
            continue

        total_selecionados = len(df_selecionados)
        resultados = {'semestre': semestre}

        # Formados
        df_formados = dados.get('formados')
        if df_formados is not None and not df_formados.empty:
            formados_nomes = df_formados['nome_inscrito'].tolist()
            selecionados_formados = df_selecionados[df_selecionados['nome_inscrito'].isin(formados_nomes)]

            num_formados = len(selecionados_formados)
            perc_formados = (num_formados / total_selecionados) * 100 if total_selecionados > 0 else 0

            resultados['perc_formados'] = round(perc_formados, 2)
            resultados['nomes_formados'] = selecionados_formados['nome_inscrito'].tolist()
        else:
            resultados['perc_formados'] = 0.0
            resultados['nomes_formados'] = []

        # Desistentes e Nunca Foram
        nomes_formados_set = set(resultados['nomes_formados'])
        df_frequencia = dados.get('frequencia')

        if df_frequencia is None or df_frequencia.empty:
            df_selecionados['total_presencas'] = 0
        else:
            df_temp = df_selecionados.merge(df_frequencia, on='nome_inscrito', how='left', suffixes=('_sel', '_freq'))

            if 'total_presencas' not in df_temp.columns:
                # Se não houver coluna total_presencas, calcula contando 'AUSENTE' ou 'PRESENTE'
                freq_cols = [c for c in df_temp.columns if c not in df_selecionados.columns and c != 'nome_inscrito']

                df_temp['total_presencas'] = df_temp.apply(
                    lambda row: sum(1 for item in row[freq_cols] if str(item).strip().upper() in ('AUSENTE', 'PRESENTE')),
                    axis=1
                )

            cols_to_keep = [c for c in df_temp.columns if not c.endswith('_freq') or c == 'total_presencas']
            df_selecionados = df_temp[cols_to_keep]

        df_selecionados['total_presencas'] = df_selecionados['total_presencas'].fillna(0)
        df_selecionados['total_presencas'] = df_selecionados['total_presencas'].astype(int)

        # Desistentes (1 a 3 presenças)
        desistentes = df_selecionados[
            (df_selecionados['total_presencas'] >= 1) &
            (df_selecionados['total_presencas'] <= 3) &
            (~df_selecionados['nome_inscrito'].isin(nomes_formados_set))
            ]
        num_desistentes = len(desistentes)
        perc_desistentes = (num_desistentes / total_selecionados) * 100 if total_selecionados > 0 else 0

        resultados['perc_desistentes'] = round(perc_desistentes, 2)
        resultados['nomes_desistentes'] = desistentes['nome_inscrito'].tolist()

        # Nunca Foram (0 presenças ou em branco)
        nunca_foram = df_selecionados[
            (df_selecionados['total_presencas'] == 0) &
            (~df_selecionados['nome_inscrito'].isin(nomes_formados_set))
            ]
        num_nunca_foram = len(nunca_foram)
        perc_nunca_foram = (num_nunca_foram / total_selecionados) * 100 if total_selecionados > 0 else 0

        resultados['perc_nunca_foram'] = round(perc_nunca_foram, 2)
        resultados['nomes_nunca_foram'] = nunca_foram['nome_inscrito'].tolist()

        # Adiciona os dados de reinscritos
        resultados['perc_multisemestre'] = round(perc_multisemestre, 2)
        resultados['nomes_multisemestre'] = nomes_multi

        # Salva no DB
        db.salvar_resultado_semestre(resultados)
        resultados_finais[semestre] = resultados

    return resultados_finais


def formatar_resultados_para_exibicao(resultados):
    """Formata os resultados do DB para o formato de string"""
    output = []

    # Ordena por semestre de forma descendente
    resultados_ordenados = sorted(resultados, key=lambda x: x[1], reverse=True)

    if not resultados_ordenados:
        return ""

        # Pega o resultado de reinscritos do primeiro registro
    primeiro_res = resultados_ordenados[0]
    perc_multi = f"{primeiro_res[8]:.2f}%"
    nomes_multi = primeiro_res[9].replace(", ", "\n- ") if primeiro_res[9] else "Nenhum"

    for res in resultados_ordenados:
        semestre = res[1]
        perc_f = res[2]
        nomes_f = res[3]
        perc_d = res[4]
        nomes_d = res[5]
        perc_n = res[6]
        nomes_n = res[7]

        # Formata as listas de nomes
        nomes_f_str = nomes_f.replace(", ", "\n- ") if nomes_f else "Nenhum"
        nomes_d_str = nomes_d.replace(", ", "\n- ") if nomes_d else "Nenhum"
        nomes_n_str = nomes_n.replace(", ", "\n- ") if nomes_n else "Nenhum"

        bloco = f"""
Semestre {semestre}
---------------------------------------------
Porcentagem de formados: {perc_f:.2f}%
Nome dos formados:
- {nomes_f_str}

Porcentagem de desistentes (frequência <= 3): {perc_d:.2f}%
Nome dos desistentes:
- {nomes_d_str}

Porcentagem de selecionados que nunca foram (frequência = 0): {perc_n:.2f}%
Nome dos selecionados que nunca foram:
- {nomes_n_str}
"""
        output.append(bloco)

    # Bloco de reinscritos no final
    bloco_multi = f"""
=============================================
DADOS GERAIS (Reinscritos)
=============================================
Porcentagem de inscritos em mais de uma aba "inscritos": {perc_multi}
Nomes dos inscritos em mais de um semestre:
- {nomes_multi}
"""
    output.append(bloco_multi)

    return "\n".join(output)


def consultar_porcentagens():
    """Função principal chamada pelo Menu"""
    try:
        # Calcula e salva os resultados no DB (e o recria se necessário)
        calcular_porcentagens_por_semestre()

        resultados_db = db.get_todos_resultados()

        if not resultados_db:
            return "Nenhum dado de semestre encontrado ou processado. Verifique o arquivo principal ('Dados_inove_mais.xlsx') na pasta 'Dados'."

        return formatar_resultados_para_exibicao(resultados_db)

    except Exception as e:
        return f"Ocorreu um erro no processamento de dados: {e}"
