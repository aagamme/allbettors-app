import pandas as pd
import streamlit as st
import plotly.express as px
import base64
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Acompanhamento Semanal - Allbettors",
    layout="wide"
)

# --------------------------------------------------------------------------
# NOMES DAS COLUNAS
# --------------------------------------------------------------------------
COLUNA_DE_DATAS = "Semana" 
COLUNA_ANO = "Ano"
COLUNA_MES_NOME = "Mês"
COLUNA_SEMANA_MES = "Semana do Mês" # <--- Nome correto e consistente
COLUNA_ID = "ID"
COLUNA_ACAO = "Ação"
COLUNA_REDE = "Rede"
COLUNA_POSTAGEM = "Postagem"
COLUNA_ASSUNTO = "Assunto"
COLUNA_VOTOS = "Votos"
# --------------------------------------------------------------------------

# --- CORES DA PALETA ---
COLOR_SIDEBAR = "#7030A0"     # Roxo
COLOR_PRIMARY = "#7030A0"     # Roxo (para elementos principais)
COLOR_CARD_BG = "#FFFFFF"     # Branco
COLOR_TEXT = "#000000"         # Preto
COLOR_SECONDARY_TEXT = "#5A5A5A" # Cinza escuro

# --- FUNÇÃO PARA PROCESSAR DATAS (COM A NOVA LÓGICA) ---
def processar_datas(df):
    if COLUNA_DE_DATAS not in df.columns:
        st.error(f"Erro Crítico: A coluna '{COLUNA_DE_DATAS}' não foi encontrada no arquivo.")
        st.stop()
    try:
        df[COLUNA_DE_DATAS] = pd.to_datetime(df[COLUNA_DE_DATAS], errors='coerce')
        df.dropna(subset=[COLUNA_DE_DATAS], inplace=True)
        
        df[COLUNA_ANO] = df[COLUNA_DE_DATAS].dt.year
        df['MesNum'] = df[COLUNA_DE_DATAS].dt.month
        df[COLUNA_MES_NOME] = df[COLUNA_DE_DATAS].dt.strftime('%b').str.capitalize()
        df['NumSemanaMes'] = (df[COLUNA_DE_DATAS].dt.day - 1) // 7 + 1
        
        df[COLUNA_SEMANA_MES] = "S" + df['NumSemanaMes'].astype(str) + "-" + df[COLUNA_MES_NOME]
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar a coluna de datas: {e}")
        st.stop()

# --- FUNÇÃO DE ESTILO COM IMAGEM DE FUNDO ---
def set_page_style(image_file):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        
        style = f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
            .stApp {{
                background-image: url("data:image/png;base64,{b64_encoded}");
                background-size: cover; background-repeat: no-repeat; background-attachment: fixed;
                font-family: 'Montserrat', sans-serif;
            }}
            .stApp > header, div[data-testid="stToolbar"], div[data-testid="stDecoration"],
            div[data-testid="stStatusWidget"] {{ display: none !important; }}
            h1 {{ color: {COLOR_TEXT} !important; text-align: center; font-weight: 700; }}
            div[data-testid="stSidebarUserContent"] {{ background-color: {COLOR_SIDEBAR}; padding-top: 2rem; }}
            div[data-testid="stSidebarUserContent"] h1, 
            div[data-testid="stSidebarUserContent"] h2,
            div[data-testid="stSidebarUserContent"] h3,
            div[data-testid="stSidebarUserContent"] label {{ color: {COLOR_CARD_BG} !important; }}
            .kpi-card {{
                background-color: {COLOR_CARD_BG}; border-radius: 12px; padding: 25px;
                text-align: center; border: 1px solid #ddd;
            }}
            .kpi-label {{ font-size: 1.1rem; color: {COLOR_SECONDARY_TEXT}; font-weight: 600; margin-bottom: 10px; }}
            .kpi-value {{ font-size: 2.8rem; font-weight: 700; color: {COLOR_PRIMARY}; }}
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error(f"ERRO: Arquivo de imagem de fundo '{image_file}' não encontrado.")
        st.stop()

# --- FUNÇÃO PARA CARREGAR OS DADOS ---
@st.cache_data
def carregar_dados(caminho_arquivo, nome_tabela):
    try:
        return pd.read_excel(caminho_arquivo, sheet_name=nome_tabela)
    except FileNotFoundError:
        st.error(f"ERRO: Arquivo de dados '{caminho_arquivo}' não encontrado.")
        return None
    except Exception as e:
        st.error(f"Erro ao ler a planilha '{nome_tabela}': {e}")
        return None

# --- EXECUÇÃO DO APP ---

# 1. Aplica o Estilo (procura o arquivo na mesma pasta do script)
set_page_style("fundo01.png")

# 2. Carrega os Dados (procura o arquivo na mesma pasta do script)
df = carregar_dados("bettors.xlsx", "Bet")

if df is None:
    st.stop()

df = processar_datas(df)

# Filtros na Barra Lateral
st.sidebar.header("Filtros")
redes_unicas = sorted(df[COLUNA_REDE].unique())
redes_selecionadas = st.sidebar.multiselect("Rede", redes_unicas, default=redes_unicas)

assuntos_unicos = sorted(df[COLUNA_ASSUNTO].unique())
assuntos_selecionados = st.sidebar.multiselect("Assunto", assuntos_unicos, default=assuntos_unicos)

st.sidebar.markdown("---")

anos_disponiveis = sorted(df[COLUNA_ANO].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

meses_df = df[df[COLUNA_ANO].isin(anos_selecionados)][['MesNum', COLUNA_MES_NOME]].drop_duplicates().sort_values('MesNum')
meses_selecionados = st.sidebar.multiselect("Mês", meses_df[COLUNA_MES_NOME].unique(), default=meses_df[COLUNA_MES_NOME].unique())

df_filtrado_para_semanas = df[
    df[COLUNA_ANO].isin(anos_selecionados) &
    df[COLUNA_MES_NOME].isin(meses_selecionados)
]
semanas_df = df_filtrado_para_semanas[['MesNum', 'NumSemanaMes', COLUNA_SEMANA_MES]].drop_duplicates().sort_values(['MesNum', 'NumSemanaMes'])
# CORREÇÃO APLICADA AQUI: Usa a variável correta 'COLUNA_SEMANA_MES'
semanas_selecionadas = st.sidebar.multiselect("Semana", semanas_df[COLUNA_SEMANA_MES].unique(), default=semanas_df[COLUNA_SEMANA_MES].unique())

# Aplica Todos os Filtros
df_filtrado = df[
    df[COLUNA_REDE].isin(redes_selecionadas) &
    df[COLUNA_ASSUNTO].isin(assuntos_selecionados) &
    df[COLUNA_ANO].isin(anos_selecionados) &
    df[COLUNA_MES_NOME].isin(meses_selecionados) &
    # CORREÇÃO APLICADA AQUI: Usa a variável correta 'COLUNA_SEMANA_MES'
    df[COLUNA_SEMANA_MES].isin(semanas_selecionadas)
]

# Área Principal do Dashboard
st.markdown("<h1>Acompanhamento Semanal - Allbettors</h1>", unsafe_allow_html=True)
st.markdown("---")

# KPIs
if not df_filtrado.empty:
    comentarios_realizados = df_filtrado[df_filtrado[COLUNA_ACAO] == 'Comentário'][COLUNA_ID].nunique()
    total_votos = int(df_filtrado[COLUNA_VOTOS].sum())

    col1, col2 = st.columns(2)
    col1.markdown(f'<div class="kpi-card"><div class="kpi-label">Comentários Realizados</div><div class="kpi-value">{comentarios_realizados}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="kpi-card"><div class="kpi-label">Total de Votos</div><div class="kpi-value">{total_votos}</div></div>', unsafe_allow_html=True)
else:
    st.warning("Nenhum dado corresponde aos filtros selecionados.")

st.markdown("<br>", unsafe_allow_html=True)

# Gráficos
if not df_filtrado.empty:
    atividades_por_assunto = df_filtrado.groupby(COLUNA_ASSUNTO)[COLUNA_ID].count().sort_values(ascending=False).reset_index()
    fig_barras = px.bar(
        atividades_por_assunto, x=COLUNA_ASSUNTO, y=COLUNA_ID,
        title="<b>Comentários por Assunto</b>", text_auto=True,
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig_barras.update_layout(
        plot_bgcolor=COLOR_CARD_BG, paper_bgcolor=COLOR_CARD_BG, font_color=COLOR_TEXT,
        xaxis=dict(categoryorder='total descending', title=''), yaxis=dict(title='Quantidade')
    )
    fig_barras.update_traces(textposition="outside")

    # CORREÇÃO APLICADA AQUI: Usa a variável correta 'COLUNA_SEMANA_MES'
    atividades_por_semana_df = df_filtrado.groupby(['Ano', 'MesNum', 'NumSemanaMes', COLUNA_SEMANA_MES])[COLUNA_ID].count().reset_index()
    atividades_por_semana_df = atividades_por_semana_df.sort_values(['Ano', 'MesNum', 'NumSemanaMes'])
    
    fig_linhas = px.line(
        atividades_por_semana_df, x=COLUNA_SEMANA_MES, y=COLUNA_ID,
        title="<b>Comentários por Semana</b>", markers=True,
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig_linhas.update_layout(
        plot_bgcolor=COLOR_CARD_BG, paper_bgcolor=COLOR_CARD_BG, font_color=COLOR_TEXT,
        xaxis=dict(title=''), yaxis=dict(title='Quantidade')
    )
    
    col_graf1, col_graf2 = st.columns(2)
    col_graf1.plotly_chart(fig_barras, use_container_width=True)
    col_graf2.plotly_chart(fig_linhas, use_container_width=True)

# Tabela de Dados
with st.expander("Clique para ver os dados detalhados"):
    st.dataframe(
        df_filtrado,
        column_config={
            "Postagem": st.column_config.LinkColumn(
                "Link da Postagem",
                display_text="Acessar Link"
            )
        },
        hide_index=True
    )