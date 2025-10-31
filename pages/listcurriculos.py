import streamlit as st
import pandas as pd
import os


# Carrega os dados
@st.cache_data
def load_curriculos_data(file_path):
    """Carrega o DataFrame de currículos com o delimitador correto."""
    try:
        # Separador é ponto e vírgula
        df = pd.read_csv(file_path, sep=';')

        return df
    except Exception as e:
        st.error(f"Erro ao carregar ou processar o arquivo CSV: {e}")
        return pd.DataFrame()  # se tiver erro, retorna dataframe vazio


# "main()"

st.set_page_config(
    page_title="Currículos",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Lista de Currículos")
st.markdown("---")

file_path = "curriculos.csv"

if not os.path.exists(file_path):
    st.error(f"Erro: O arquivo de vagas '{file_path}' não foi encontrado.")
    st.warning("Certifique-se de que o arquivo CSV está na mesma pasta que este script Streamlit.")
    st.stop()

# Carrega os dados
df_curriculos = load_curriculos_data(file_path)

if df_curriculos.empty:
    st.warning("Não foi possível carregar os dados de curriculos. Verifique o arquivo CSV.")
    st.stop()

st.info(f"O sistema encontrou um total de **{len(df_curriculos)}** currículos.")

# Sidebar
st.sidebar.header("Filtros de Currículos")
search_query = st.sidebar.text_input("Buscar por Formação/Experiência/Skill/Idioma", "").lower()

# Aplica os filtros
df_filtered = df_curriculos.copy()

# Filtro de busca textual
if search_query:
    df_filtered = df_filtered[
        df_filtered['formacao'].str.lower().str.contains(search_query) |
        df_filtered['experiencia'].str.lower().str.contains(search_query) |
        df_filtered['skills'].str.lower().str.contains(search_query) |
        df_filtered['idiomas'].str.lower().str.contains(search_query)
        ]


st.subheader(f"Currículos Encontrados: {len(df_filtered)}")

if df_filtered.empty:
    st.warning("Nenhum currículo encontrado com os filtros e critérios de busca atuais.")
    st.stop()


# De fato mostrar os curriculos

# For para filtrar os curriculos
for index, row in df_filtered.iterrows():
    # Título do expander: Nome | Formação
    title = f"**{row['nome']}** - **{row['formacao']}**"

    with st.expander(title):

        st.markdown(f"**👔 Experiência:** {row['experiencia']}")
        st.markdown(f"**💻 Skills:** {row['skills']} - **📖 Idiomas:** {row['idiomas']}")
        st.markdown(f"**✅ Certificações:** {row['certificacoes']}")
        st.markdown(f"**🏢 Empresas Prévias:** {row['empresas_previas']}")

        st.markdown("---")

        st.markdown("**Resumo Profissional:**")
        st.markdown(row['resumo'])

        st.markdown("---")

        st.markdown(f"**📨 Email:** {row['email']} - ☎️ **Telefone:** {row['telefone']}")
