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
        pass

#--- GESTÃO DE SESSÃO (visitante vs logado) ---
#Não bloqueamos o acesso, apenas identificamos quem é
is_logged_in = st.session_state.get('logged_in', False)
tipo_usuario = st.session_state.get('tipo_usuario', 'visitante')
empresa_usuario = st.session_state.get('empresa', None)

@st.cache_data
def load_vagas_data(filtro_empresa=None):
    """
    Carrega vagas. Se filtro_empresa for passado, filtra no MongoDB.
    """
    col_vagas, _, _ = get_collections()
    if col_vagas is None:
        return pd.DataFrame()

    try:
        #LÓGICA DE FILTRO DE NEGÓCIO DIRETO NO MONGO
        query = {}
        if filtro_empresa:
            #Busca case-insensitive para garantir
            query = {"empresa": {"$regex": f"^{filtro_empresa}$", "$options": "i"}}

        cursor = col_vagas.find(query)
        vagas_list = list(cursor)
        df = pd.DataFrame(vagas_list)

        if df.empty:
            return df

        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)

        df['salario_float'] = pd.to_numeric(df['salario'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar vagas: {e}")
        return pd.DataFrame()


#"main()"
st.set_page_config(page_title="Dashboard de vagas", page_icon="💼", layout="wide")

#Título dinâmico
if is_logged_in and tipo_usuario == 'empregador':
    st.title(f"📊 Minhas vagas ({empresa_usuario})")
    #Carrega SÓ as vagas da empresa associada ao empregador
    df_vagas = load_vagas_data(filtro_empresa=empresa_usuario)
else:
    st.title("📊 Mural de vagas")
    if not is_logged_in:
        st.info("💡 Dica: faça login para acessar funcionalidades avançadas ou cadastrar seu currículo.")
    #Carrega TUDO (Candidato/Admin/Visitante)
    df_vagas = load_vagas_data(filtro_empresa=None)

#Botão de atualização
if st.sidebar.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

if df_vagas.empty:
    if tipo_usuario == 'empregador':
        st.info(f"Você ainda não cadastrou nenhuma vaga para {empresa_usuario}.")
        st.markdown("Vá em **Cadastrar Vaga** no menu lateral.")
    else:
        st.warning("Nenhuma vaga encontrada no sistema.")
    st.stop()

#--- APLICAÇÃO DOS FILTROS (mantido igual, mas agora sobre o df já filtrado) ---
st.sidebar.header("Filtros avançados")

#1. Filtro de texto
search_query = st.sidebar.text_input("🔍 Buscar (Título/Empresa/Cidade)", "").lower()

#2. Filtro de tipo de contratação
if 'tipo_contratacao' in df_vagas.columns:
    tipos_unicos = ['Todos'] + list(df_vagas['tipo_contratacao'].unique())
    tipo_selecionado = st.sidebar.selectbox("📋 Tipo de contratação", options=tipos_unicos)
else:
    tipo_selecionado = 'Todos'

#3. Filtro de aalário (alider)
if 'salario_float' in df_vagas.columns and not df_vagas['salario_float'].isnull().all():
    min_sal = float(df_vagas['salario_float'].min())
    max_sal = float(df_vagas['salario_float'].max())
    #Margem de segurança para o slider não quebrar se min==max
    if min_sal == max_sal:
        max_sal += 1000.0

    salario_range = st.sidebar.slider(
        "💰 Faixa Salarial (R$)",
        min_value=0.0,
        max_value=max_sal + 1000.0,
        value=(0.0, max_sal + 1000.0),
        step=100.0
    )
else:
    salario_range = None

#--- APLICAÇÃO DOS FILTROS ---
df_filtered = df_vagas.copy()

#Filtro salário
if salario_range:
    df_filtered = df_filtered[
        (df_filtered['salario_float'] >= salario_range[0]) &
        (df_filtered['salario_float'] <= salario_range[1]) |
        (df_filtered['salario_float'].isna()) ] #Mantém salários não informados/negociáveis

#Filtro tipo contratação
if tipo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['tipo_contratacao'] == tipo_selecionado]

#Filtro texto
if search_query:
    df_filtered = df_filtered[
        df_filtered['titulo'].str.lower().str.contains(search_query, na=False) |
        df_filtered['descricao'].str.lower().str.contains(search_query, na=False) |
        df_filtered['empresa'].str.lower().str.contains(search_query, na=False) |
        df_filtered['cidade'].str.lower().str.contains(search_query, na=False)
        ]

#Métricas
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

#--- LISTAGEM ---
for index, row in df_filtered.iterrows():
    salario_display = "A combinar"
    if pd.notna(row['salario_float']) and row['salario_float'] > 0:
        try:
            salario_display = locale.currency(row['salario_float'], grouping=True, symbol=True)
        except:
            salario_display = f"R$ {row['salario_float']:,.2f}"

        #Header do card com cor baseada no tipo
        tipo_emoji = "💼" if row['tipo_contratacao'] == "CLT" else "📄"
        title = f"{tipo_emoji} **{row['titulo']}** | {row['empresa']}"

    with st.expander(title):
        #Layout em colunas dentro do card para ficar mais bonito
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"**📍 Local:** {row['cidade']} - {row['estado']}")
            st.markdown(f"**💰 Salário:** {salario_display}")
            st.markdown(f"**📝 Tipo de contrato:** {row['tipo_contratacao']}")
        with c2:
            st.caption("Descrição e requisitos")
            st.markdown(row['descricao'])
            skills = row.get('skills', [])
            if isinstance(skills, list) and skills:
                st.markdown(f"**🛠 Skills:** {', '.join(skills)}")
            elif isinstance(skills, str):
                st.markdown(f"**🛠 Skills:** {skills}")

        st.caption(f"ID: {row.get('id', 'N/A')}")