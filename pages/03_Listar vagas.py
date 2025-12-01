import streamlit as st
import pandas as pd
from db_connection import get_collections
import locale

#Config de localidade (para moeda)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        pass  #Ignora se não conseguir definir


#Carregamento de dados
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
        df = pd.DataFrame(vagas_list)

        if df.empty:
            return df

        #Converte o ObjectId para string (útil para exibição)
        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)

        #Converte 'salario' para numérico
        df['salario_float'] = pd.to_numeric(df['salario'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Erro ao carregar vagas do MongoDB: {e}")
        return pd.DataFrame()


#"main()"
st.set_page_config(
    page_title="Dashboard de vagas",
    page_icon="💼",
    layout="wide"
)

st.title("📊 Dashboard de vagas")
st.markdown("Visualize e filtre as oportunidades disponíveis em tempo real.")

#Botão de atualização
if st.sidebar.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

df_vagas = load_vagas_data()

if df_vagas.empty:
    st.warning("Nenhuma vaga encontrada no banco de dados.")
    st.stop()

#--- FILTROS ---
st.sidebar.header("Filtros Avançados")

#1. Filtro de Texto
search_query = st.sidebar.text_input("🔍 Buscar (Título/Empresa)", "").lower()

#2. Filtro de Contratação
tipos_contratacao_unicos = ['Todos'] + list(df_vagas['tipo_contratacao'].unique())
tipo_selecionado = st.sidebar.selectbox("📋 Tipo de Contratação", options=tipos_contratacao_unicos)

#3. Filtro de Salário (slider duplo)
min_sal = float(df_vagas['salario_float'].min()) if not df_vagas['salario_float'].isnull().all() else 0.0
max_sal = float(df_vagas['salario_float'].max()) if not df_vagas['salario_float'].isnull().all() else 10000.0
salario_range = st.sidebar.slider(
    "💰 Faixa salarial (R$)",
    min_value=0.0,
    max_value=max_sal + 1000,  #Margem
    value=(min_sal, max_sal),
    step=100.0
)

#--- APLICAÇÃO DOS FILTROS ---
df_filtered = df_vagas.copy()

#Filtro salário
df_filtered = df_filtered[
    (df_filtered['salario_float'] >= salario_range[0]) &
    (df_filtered['salario_float'] <= salario_range[1]) |
    (df_filtered['salario_float'].isna())  #Mantém salários não informados
    ]

#Filtro texto
if search_query:
    df_filtered = df_filtered[
        df_filtered['titulo'].str.lower().str.contains(search_query, na=False) |
        df_filtered['descricao'].str.lower().str.contains(search_query, na=False) |
        df_filtered['empresa'].str.lower().str.contains(search_query, na=False) |
        df_filtered['cidade'].str.lower().str.contains(search_query, na=False) ]

#Filtro tipo
if tipo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['tipo_contratacao'] == tipo_selecionado]

#--- METRICAS (KPIs) ---
st.markdown("---")
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric(label="Total de vagas", value=len(df_filtered))

with col_kpi2:
    media_salarial = df_filtered['salario_float'].mean()
    val_media = f"R$ {media_salarial:,.2f}" if pd.notna(media_salarial) else "N/A"
    st.metric(label="Média salarial", value=val_media)

with col_kpi3:
    top_cidade = df_filtered['cidade'].mode()[0] if not df_filtered.empty else "N/A"
    st.metric(label="Cidade com mais vagas", value=top_cidade)

st.markdown("---")

if df_filtered.empty:
    st.warning("Nenhuma vaga encontrada com os filtros atuais.")
    st.stop()

#--- LISTAGEM ---
for index, row in df_filtered.iterrows():
    salario_display = "A combinar"
    if pd.notna(row['salario_float']) and row['salario_float'] > 0:
        try:
            salario_display = locale.currency(row['salario_float'], grouping=True, symbol=True)
        except Exception:
            salario_display = f"R$ {row['salario_float']:,.2f}"

    #Header do card com cor baseada no tipo
    tipo_emoji = "💼" if row['tipo_contratacao'] == "CLT" else "📄"
    title = f"{tipo_emoji} **{row['titulo']}** | {row['empresa']}"

    with st.expander(title):
        #Layout em colunas dentro do card para ficar mais bonito
        c1, c2 = st.columns([1, 2])

        with c1:
            st.caption("Detalhes")
            st.markdown(f"**📍 Local:** {row['cidade']} - {row['estado']}")
            st.markdown(f"**💰 Salário:** {salario_display}")
            st.markdown(f"**📝 Contrato:** {row['tipo_contratacao']}")

        with c2:
            st.caption("Descrição & Requisitos")
            st.markdown(row['descricao'])

            skills = row.get('skills', [])
            if isinstance(skills, list) and skills:
                st.markdown(f"**🛠 Skills:** {', '.join(skills)}")
            elif isinstance(skills, str):
                st.markdown(f"**🛠 Skills:** {skills}")

        st.caption(f"ID: {row.get('id', 'N/A')}")