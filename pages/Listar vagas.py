import streamlit as st
import pandas as pd
import os


#Carrega os dados
@st.cache_data
def load_vagas_data(file_path):
    """Carrega o DataFrame de vagas com o delimitador correto."""
    try:
        #Separador é ponto e vírgula
        df = pd.read_csv(file_path, sep=';')

        #Tira o R$ e troca , por . no salário, para ficar no padrão do pandas
        df['salario_clean'] = df['salario'].astype(str).str.replace(r'[^\d,]', '', regex=True).str.replace(',', '.')

        #Transforma o salario formatado em float (se tiver algum problema, deixa como NaN)
        df['salario_float'] = pd.to_numeric(df['salario_clean'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Erro ao carregar ou processar o arquivo CSV: {e}")
        return pd.DataFrame()  #se tiver erro, retorna dataframe vazio


#"main()"

st.set_page_config(
    page_title="Listagem de vagas",
    page_icon="💼",
    layout="wide"
)

st.title("Lista de Vagas em Aberto")
st.markdown("---")

file_path = "vagas.csv"

if not os.path.exists(file_path):
    st.error(f"Erro: O arquivo de vagas '{file_path}' não foi encontrado.")
    st.warning("Certifique-se de que o arquivo CSV está na mesma pasta que este script Streamlit.")
    st.stop()

#Carrega os dados
df_vagas = load_vagas_data(file_path)

if df_vagas.empty:
    st.warning("Não foi possível carregar os dados de vagas. Verifique o arquivo CSV.")
    st.stop()

st.info(f"O sistema encontrou um total de **{len(df_vagas)}** vagas abertas.")

#Sidebar
st.sidebar.header("Filtros de Vagas")
search_query = st.sidebar.text_input("Buscar por Título/Descrição/Empresa/Cidade", "").lower()

tipos_unicos = ['Todos'] + sorted(df_vagas['tipo_contratacao'].unique().tolist())
tipo_selecionado = st.sidebar.selectbox("Tipo de Contratação", tipos_unicos)

#Aplica os filtros
df_filtered = df_vagas.copy()

#Filtro de busca textual
if search_query:
    df_filtered = df_filtered[
        df_filtered['titulo'].str.lower().str.contains(search_query) |
        df_filtered['descricao'].str.lower().str.contains(search_query) |
        df_filtered['empresa'].str.lower().str.contains(search_query) |
        df_filtered['cidade'].str.lower().str.contains(search_query)
        ]

#Filtro por tipo de contratação
if tipo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['tipo_contratacao'] == tipo_selecionado]

st.subheader(f"Vagas Encontradas: {len(df_filtered)}")

if df_filtered.empty:
    st.warning("Nenhuma vaga encontrada com os filtros e critérios de busca atuais.")
    st.stop()


# De fato mostrar as vagas

# For para filtrar as vagas
for index, row in df_filtered.iterrows():
    # Formata o salario
    # Usa o valor original (string) se a conversão der ruim
    salario_display = row['salario']
    if pd.notna(row['salario_float']):
        salario_display = f"R$ {row['salario_float']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    # Título do expander: Título da Vaga | Empresa | Cidade/Estado
    title = f"**{row['titulo']}** na **{row['empresa']}** - {row['cidade']} ({row['estado']})"

    with st.expander(title):
        st.markdown(f"**💰 Salário:** {salario_display} | **🤝 Contrato:** {row['tipo_contratacao']}")
        st.markdown(f"**📍 Local:** {row['cidade']} - {row['estado']}")
        st.markdown(f"**🛠️ Skills/Requisitos:** {row['skills']}")

        st.markdown("---")

        st.markdown("**Descrição da Vaga:**")
        st.markdown(row['descricao'])