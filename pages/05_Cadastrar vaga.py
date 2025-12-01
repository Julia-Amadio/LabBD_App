import streamlit as st
from db_connection import get_collections, create_embedding
from pymongo.errors import PyMongoError
import datetime

#------- CONTROLE DE ACESSO -------
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Faça login.")
    st.stop()

tipo_usuario = st.session_state['tipo_usuario']
empresa_usuario = st.session_state.get('empresa')

if tipo_usuario == 'candidato':
    st.error("⛔ ACESSO RESTRITO: candidatos não podem cadastrar vagas!")
    st.stop()
#----------------------------------

#Configuração da página
st.set_page_config(page_title="Cadastro de Vagas", page_icon="🚀", layout="wide")

st.title("🚀 Cadastro de nova vaga")
st.write("Preencha o formulário abaixo para adicionar uma nova vaga ao banco de dados.")

#Constantes de opções
TIPOS_CONTRATACAO = ["CLT", "PJ", "Estágio", "Temporário"]
ESTADOS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

#Formulário
with st.form(key="vaga_form", clear_on_submit=True):
    st.subheader("Informações principais")
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("**Título da vaga**", placeholder="Ex: Engenheiro de Software Sênior")
        #Se logado como empregador, o campo vem preenchido e desabilitado
        #Se for Admin, o campo é livre
        val_empresa = empresa_usuario if tipo_usuario == 'empregador' else ""
        disable_empresa = True if tipo_usuario == 'empregador' else False
        empresa = st.text_input("**Empresa**", value=val_empresa, disabled=disable_empresa)
        salario = st.number_input("**Salário (R$)**", min_value=0.0, step=100.0, format="%.2f")
    with col2:
        cidade = st.text_input("**Cidade**", placeholder="Ex: São Paulo")
        estado = st.selectbox("**Estado (UF)**", options=ESTADOS_BRASIL)
        tipo_contratacao = st.selectbox("**Tipo de contratação**", options=TIPOS_CONTRATACAO)

    st.subheader("Descrição e requisitos")
    descricao = st.text_area("**Descrição da vaga**", height=150, placeholder="Descreva as responsabilidades...")

    skills_input = st.text_area(
        "**Skills necessárias (uma por linha)**",
        height=100,
        placeholder="Python\nReact\nMongoDB\nDocker"
    )

    submitted = st.form_submit_button("Cadastrar vaga")

#Lógica de salvamento
if submitted:
    #Se for empregador, garante que a empresa usada é a dele mesmo se tentar algum bypassing
    if tipo_usuario == 'empregador':
        empresa = empresa_usuario

    #Validação
    if not all([titulo, empresa, tipo_contratacao, skills_input, cidade, estado, descricao]):
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
    else:
        try:
            col_vagas, _, _ = get_collections()
            if col_vagas is None:
                st.error("Não foi possível conectar à coleção de vagas.")
                st.stop()

            #Lógica para gerar ID sequencial
            last_doc = col_vagas.find_one(sort=[("id", -1)])
            novo_id = 1
            if last_doc and "id" in last_doc:
                novo_id = int(last_doc["id"]) + 1

            #Converte skills de string para lista
            skills_list = [s.strip() for s in skills_input.split('\n') if s.strip()]

            #--------- GERAÇÃO DE EMBEDDING ---------
            embedding_to_save = []
            st.info("Gerando embedding para a vaga...")
            text_to_embed = f"Título: {titulo}. Descrição: {descricao}. Skills: {', '.join(skills_list)}"
            embedding = create_embedding(text_to_embed)

            if embedding:
                embedding_to_save = embedding
                st.success("✨ Embedding gerado com sucesso!")
            else:
                st.warning("⚠️ Cota do Google AI Studio excedida. O registro foi salvo no banco sem embedding.")
            #----------------------------------------

            #Montar o documento para o MongoDB
            nova_vaga_doc = {
                "id": novo_id,
                "titulo": titulo,
                "descricao": descricao,
                "cidade": cidade,
                "estado": estado.upper(),
                "tipo_contratacao": tipo_contratacao,
                "salario": salario,
                "empresa": empresa,
                "skills": skills_list,
                "embedding": embedding_to_save, #Salva o vetor ou lista vazia
                "data_cadastro": datetime.datetime.now(datetime.timezone.utc)
            }

            #Inserir no banco
            result = col_vagas.insert_one(nova_vaga_doc)

            st.success(f"🎉 Vaga '{titulo}' (ID: {novo_id}) cadastrada com sucesso!")
            st.info(f"ID do MongoDB: `{result.inserted_id}`")
            st.balloons()

            st.cache_data.clear()

        except PyMongoError as e:
            st.error(f"Erro ao salvar no MongoDB: {e}")
        except Exception as e:
            st.error(f"Um erro inesperado ocorreu: {e}")