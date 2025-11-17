import streamlit as st
import pandas as pd
from db_connection import get_collections  #Importa nossa nova função
import locale

#Config de localidade (para moeda)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        pass  #Ignora se não conseguir definir


#Carregamento de dados (agora do MongoDB)
@st.cache_data
def load_vagas_data():
    """Carrega o DataFrame de vagas a partir do MongoDB Atlas."""
    col_vagas, _, _ = get_collections()
    if col_vagas is None:
        st.error("Não foi possível conectar à coleção de vagas.")
        return pd.DataFrame()  #Retorna DF vazio

    try:
        #Busca todos os documentos da coleção
        cursor = col_vagas.find()
        vagas_list = list(cursor)

        #Converte a lista de dicionários em DataFrame
        df = pd.DataFrame(vagas_list)

        if df.empty:
            return df

        #Converte o ObjectId para string (útil para exibição)
        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)

        #Converte 'salario' para numérico (JSON já vem numérico, mas é bom garantir)
        df['salario_float'] = pd.to_numeric(df['salario'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Erro ao carregar vagas do MongoDB: {e}")
        return pd.DataFrame()


#"main()"
st.set_page_config(
    page_title="Listagem de vagas",
    page_icon="💼",
    layout="wide"
)

st.title("Lista de Vagas em Aberto (MongoDB)")
st.markdown("---")

df_vagas = load_vagas_data()

if df_vagas.empty:
    st.warning("Nenhuma vaga encontrada no banco de dados.")
    st.stop()

#FILTROS (lógica tradicional do Pandas)
st.sidebar.header("Filtros")
search_query = st.sidebar.text_input("Buscar por Título/Empresa/Cidade", "").lower()

tipos_contratacao_unicos = ['Todos'] + list(df_vagas['tipo_contratacao'].unique())
tipo_selecionado = st.sidebar.selectbox(
    "Filtrar por Tipo de Contratação",
    options=tipos_contratacao_unicos
)

#LÓGICA DE FILTRO (Pandas)
df_filtered = df_vagas.copy()

if search_query:
    df_filtered = df_filtered[
        df_filtered['titulo'].str.lower().str.contains(search_query, na=False) |
        df_filtered['descricao'].str.lower().str.contains(search_query, na=False) |
        df_filtered['empresa'].str.lower().str.contains(search_query, na=False) |
        df_filtered['cidade'].str.lower().str.contains(search_query, na=False)
        ]

if tipo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['tipo_contratacao'] == tipo_selecionado]

st.subheader(f"Vagas Encontradas: {len(df_filtered)}")

if df_filtered.empty:
    st.warning("Nenhuma vaga encontrada com os filtros e critérios de busca atuais.")
    st.stop()

#Exibição das Vagas
for index, row in df_filtered.iterrows():
    salario_display = "Não informado"
    if pd.notna(row['salario_float']) and row['salario_float'] > 0:
        try:
            salario_display = locale.currency(row['salario_float'], grouping=True, symbol=True)
        except Exception:
            salario_display = f"R$ {row['salario_float']:,.2f}"

    title = f"**{row['titulo']}** na **{row['empresa']}** - {row['cidade']} ({row['estado']})"

    with st.expander(title):
        st.markdown(f"**💰 Salário:** {salario_display} | **✍️ Contratação:** {row['tipo_contratacao']}")

        #'skills' agora é uma lista vinda do Mongo
        if isinstance(row['skills'], list):
            skills_display = ", ".join(row['skills'])
        else:
            skills_display = str(row.get('skills', 'N/A'))

        st.markdown(f"**🛠️ Skills:** {skills_display}")
        st.markdown(f"**Descrição:**\n{row['descricao']}")
        st.caption(f"ID no Bando de Dados (Mongo): {row['_id']}")