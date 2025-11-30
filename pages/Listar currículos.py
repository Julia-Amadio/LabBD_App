import streamlit as st
import pandas as pd
from db_connection import get_collections


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


#Funções auxiliares
def join_list_field(field):
    if isinstance(field, list):
        return ' '.join(field).lower()
    elif isinstance(field, str):
        return field.lower()
    return ""


def format_list_display(data_list):
    if isinstance(data_list, list) and data_list:
        return ", ".join(data_list)
    elif isinstance(data_list, str) and data_list:
        return data_list
    return "N/A"


#"main()"
st.set_page_config(
    page_title="Banco de talentos",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Banco de talentos")
st.markdown("Explore os perfis cadastrados no sistema.")

if st.sidebar.button("🔄 Atualizar lista"):
    st.cache_data.clear()
    st.rerun()

df_curriculos = load_curriculos_data()

if df_curriculos.empty:
    st.info("Ainda não há currículos cadastrados.")
    st.stop()

#--- FILTROS ---
st.sidebar.header("Filtros")
search_query = st.sidebar.text_input("🔍 Buscar (Skill, Idioma, Formação)", "").lower()

df_filtered = df_curriculos.copy()

if search_query:
    df_filtered['search_skills'] = df_filtered['skills'].apply(join_list_field)
    df_filtered['search_idiomas'] = df_filtered['idiomas'].apply(join_list_field)

    df_filtered = df_filtered[
        df_filtered['formacao'].str.lower().str.contains(search_query, na=False) |
        df_filtered['experiencia'].str.lower().str.contains(search_query, na=False) |
        df_filtered['search_skills'].str.contains(search_query, na=False) |
        df_filtered['search_idiomas'].str.contains(search_query, na=False)
        ]

#KPI Simples
st.metric("Candidatos Encontrados", len(df_filtered))
st.markdown("---")

if df_filtered.empty:
    st.warning("Nenhum currículo encontrado com os filtros atuais.")
    st.stop()

#--- EXIBIÇÃO ---
for index, row in df_filtered.iterrows():
    title = f"**{row['nome']}** - {row.get('formacao', 'Formação N/A')}"

    with st.expander(title):
        #Layout em colunas: Dados profissionais | Contato
        col_dados, col_contato = st.columns([2, 1])

        with col_dados:
            st.markdown("#### 💼 Perfil profissional")

            skills = format_list_display(row.get('skills', []))
            idiomas = format_list_display(row.get('idiomas', []))

            if skills != "N/A": st.markdown(f"**🛠 Skills:** {skills}")
            if idiomas != "N/A": st.markdown(f"**🗣 Idiomas:** {idiomas}")

            st.markdown(f"**Experiência:** {row.get('experiencia', 'N/A')}")
            st.info(f"**Resumo:** {row.get('resumo', 'N/A')}")

        with col_contato:
            st.markdown("#### 📞 Contato")
            st.markdown(f"**Email:** {row.get('email', 'N/A')}")
            st.markdown(f"**Tel:** {row.get('telefone', 'N/A')}")

        st.caption(f"ID: {row.get('id', 'N/A')}")