import streamlit as st
from db_connection import get_collections, create_embedding  #Importa nossas novas funções
from pymongo.errors import PyMongoError
import datetime

#Config da página
st.set_page_config(
    page_title="Cadastro de vagas",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Cadastro de nova Vaga (com Embeddings)")
st.write("Preencha o formulário abaixo para adicionar uma nova vaga ao banco de dados.")
st.write("Caso a cota de requisições do Google AI Studio tenha sido excedida, o Embedding não será gerado e a Vaga será salva SEM a função de busca por IA.")

#Constantes de opções
TIPOS_CONTRATACAO = ["CLT", "PJ", "Estágio", "Temporário"]

#Formulário
with st.form(key="vaga_form", clear_on_submit=True):
    st.subheader("Informações principais")
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("**Título da vaga**", placeholder="Ex: Engenheiro de Software sênior")
        empresa = st.text_input("**Empresa**", placeholder="Ex: Google")
        salario = st.number_input("**Salário (R$)**", min_value=0.0, step=100.0, format="%.2f")
    with col2:
        cidade = st.text_input("**Cidade**", placeholder="Ex: São Paulo")
        estado = st.text_input("**Estado (UF)**", max_chars=2, placeholder="Ex: SP")
        tipo_contratacao = st.selectbox("**Tipo de contratação**", options=TIPOS_CONTRATACAO)

    st.subheader("Descrição e requisitos")
    descricao = st.text_area("**Descrição da vaga**", height=150, placeholder="Descreva as responsabilidades...")

    #MODIFICADO: Usando Text Area para salvar como LISTA
    skills_input = st.text_area(
        "**Skills Necessárias (uma por linha)**",
        height=100,
        placeholder="Python\nReact\nMongoDB\nDocker"
    )

    submitted = st.form_submit_button("Cadastrar vaga")

#Lógica de salvamento, agora com Mongo e Embeddings
if submitted:
    #Validação
    if not all([titulo, empresa, tipo_contratacao, skills_input, cidade, estado, descricao]):
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
    else:
        try:
            col_vagas, _, _ = get_collections()
            if col_vagas is None:
                st.error("Não foi possível conectar à coleção de vagas.")
                st.stop()

            ############LÓGICA PARA GERAR NOVO ID NUMÉRICO############
            last_doc = col_vagas.find_one(sort=[("id", -1)])

            novo_id = 1  #Padrão se a coleção estiver vazia
            if last_doc and "id" in last_doc:
                novo_id = int(last_doc["id"]) + 1
            ##########################################################

            #Converte skills de string (uma por linha) para lista
            skills_list = [s.strip() for s in skills_input.split('\n') if s.strip()]

            #*** USO DE EMBEDDING ***
            st.write("Tentando gerar embedding para a vaga...")
            text_to_embed = f"Título: {titulo}. Descrição: {descricao}. Skills: {', '.join(skills_list)}"

            embedding = create_embedding(text_to_embed)

            ############LÓGICA DE FALHA MODIFICADA (Tolerante)############
            embedding_to_save = []  #Define um valor padrão (lista vazia)
            if embedding is None:
                st.warning(
                    "⚠️ AVISO: Falha ao gerar embedding (Quota Excedida?). A vaga será salva SEM a função de busca por IA.")
            else:
                st.success("Embedding gerado com sucesso!")
                embedding_to_save = embedding
            ##############################################################

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
                "embedding": embedding_to_save,  #Salva o vetor (ou lista vazia)
                "data_cadastro": datetime.datetime.now(datetime.timezone.utc)
            }

            #Inserir no banco
            result = col_vagas.insert_one(nova_vaga_doc)

            st.success(f"🎉 Vaga '{titulo}' (ID: {novo_id}) cadastrada com sucesso!")
            st.info(f"ID da Vaga no MongoDB: `{result.inserted_id}`")
            st.balloons()

            #Limpa o cache para a lista ser atualizada automaticamente
            st.cache_data.clear()

        except PyMongoError as e:
            st.error(f"Erro ao salvar no MongoDB: {e}")
        except Exception as e:
            st.error(f"Um erro inesperado ocorreu: {e}")