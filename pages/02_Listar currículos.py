import streamlit as st
import pandas as pd
from db_connection import get_collections

#--- CONTROLE DE ACESSO ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Por favor, faça login para acessar esta página.")
    st.stop()

tipo_usuario = st.session_state['tipo_usuario']

#Regra: candidato não pode ver lista geral de currículos
if tipo_usuario == 'candidato':
    st.error("⛔ ACESSO RESTRITO: candidatos não têm permissão para visualizar o banco de talentos.")
    st.info("Para ver seus dados, acesse a página 'Meu currículo'.")
    st.stop()
#--------------------------

#Carregamento de dados
@st.cache_data
def load_curriculos_data():
    _, col_curriculos, _ = get_collections()
    if col_curriculos is None:
        st.error("Não foi possível conectar à coleção de currículos.")
        return pd.DataFrame()

    try:
        #Admin e empregador veem tudo
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


def format_list_display(data_list):
    if isinstance(data_list, list) and data_list:
        return ", ".join(data_list)
    elif isinstance(data_list, str) and data_list:
        return data_list
    return "N/A"


#--- "main()" ---
st.set_page_config(page_title="Banco de talentos", page_icon="👥", layout="wide")
st.title("👥 Banco de talentos")
st.markdown("Explore os currículos cadastrados no sistema.")

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

#Lógica de filtro Pandas (simplificada para brevidade)
if search_query:
    #Função lambda rápida para juntar listas
    to_str = lambda x: ' '.join(x).lower() if isinstance(x, list) else str(x).lower()

    mask = (
            df_filtered['formacao'].apply(to_str).str.contains(search_query) |
            df_filtered['skills'].apply(to_str).str.contains(search_query) |
            df_filtered['idiomas'].apply(to_str).str.contains(search_query)
    )
    df_filtered = df_filtered[mask]

st.metric("Candidatos encontrados", len(df_filtered))
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