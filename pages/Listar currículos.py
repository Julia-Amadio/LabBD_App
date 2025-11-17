import streamlit as st
import pandas as pd
from db_connection import get_collections  #Importa nossa nova função


#Carregamento de dados (agora do Mongo)
@st.cache_data
def load_curriculos_data():
    """Carrega o DataFrame de currículos a partir do MongoDB Atlas."""
    _, col_curriculos, _ = get_collections()
    if col_curriculos is None:
        st.error("Não foi possível conectar à coleção de currículos.")
        return pd.DataFrame()

    try:
        cursor = col_curriculos.find()
        curriculos_list = list(cursor)
        df = pd.DataFrame(curriculos_list)

        if df.empty:
            return df

        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)

        return df
    except Exception as e:
        st.error(f"Erro ao carregar currículos do MongoDB: {e}")
        return pd.DataFrame()


#Funções auxiliares para lidar com listas
def join_list_field(field):
    """Converte um campo (que pode ser lista ou string) em uma string única para busca."""
    if isinstance(field, list):
        return ' '.join(field).lower()
    elif isinstance(field, str):
        return field.lower()
    return ""


def format_list_display(data_list):
    """Formata uma lista para exibição bonita."""
    if isinstance(data_list, list) and data_list:
        return ", ".join(data_list)
    elif isinstance(data_list, str) and data_list:
        return data_list
    return "N/A"


#"main()"
st.set_page_config(
    page_title="Listagem de currículos",
    page_icon="📜",
    layout="wide"
)

st.title("Lista de Currículos (MongoDB)")
st.markdown("---")

df_curriculos = load_curriculos_data()

if df_curriculos.empty:
    st.warning("Nenhum currículo encontrado no banco de dados.")
    st.stop()

#FILTROS
st.sidebar.header("Filtros")
search_query = st.sidebar.text_input("Buscar por Formação/Experiência/Skill/Idioma", "").lower()

df_filtered = df_curriculos.copy()

if search_query:
    #Cria colunas "pesquisáveis" juntando as listas
    df_filtered['search_skills'] = df_filtered['skills'].apply(join_list_field)
    df_filtered['search_idiomas'] = df_filtered['idiomas'].apply(join_list_field)

    df_filtered = df_filtered[
        df_filtered['formacao'].str.lower().str.contains(search_query, na=False) |
        df_filtered['experiencia'].str.lower().str.contains(search_query, na=False) |
        df_filtered['search_skills'].str.contains(search_query, na=False) |
        df_filtered['search_idiomas'].str.contains(search_query, na=False)
        ]

st.subheader(f"Currículos Encontrados: {len(df_filtered)}")

if df_filtered.empty:
    st.warning("Nenhum currículo encontrado com os filtros e critérios de busca atuais.")
    st.stop()

#Exibição
for index, row in df_filtered.iterrows():
    title = f"**{row['nome']}** - **{row['formacao']}**"

    with st.expander(title):
        email = row.get('email', 'N/A')
        telefone = row.get('telefone', 'N/A')

        skills_display = format_list_display(row.get('skills', []))
        idiomas_display = format_list_display(row.get('idiomas', []))
        empresas_display = format_list_display(row.get('empresas_previas', []))
        cert_display = format_list_display(row.get('certificacoes', []))

        st.markdown(f"**📧 Email:** {email} | **📞 Telefone:** {telefone}")
        st.markdown(f"**👔 Experiência:** {row.get('experiencia', 'N/A')}")
        st.markdown(f"**💻 Skills:** {skills_display}")
        st.markdown(f"**📖 Idiomas:** {idiomas_display}")
        st.markdown(f"**🏢 Empresas Anteriores:** {empresas_display}")
        st.markdown(f"**🏅 Certificações:** {cert_display}")
        st.markdown(f"**Resumo:**\n{row.get('resumo', 'N/A')}")
        st.caption(f"ID no Bando de Dados (Mongo): {row['_id']}")