import streamlit as st
from db_connection import get_collections, create_embedding  #Importa nossas novas funções
from pymongo.errors import PyMongoError
import datetime

#Configuração da página
st.set_page_config(
    page_title="Cadastro de currículos",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Cadastro de novo Currículo (com Embeddings)")
st.write("Preencha o formulário abaixo para adicionar um novo currículo ao banco de dados.")
st.write("Caso a cota de requisições do Google AI Studio tenha sido excedida, o Embedding não será gerado e o Currículo será salvo SEM a função de busca por IA.")

#Formulário
with st.form(key="curriculo_form", clear_on_submit=True):
    st.subheader("Informações pessoais")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("**Nome completo**", placeholder="Ex: Ana da Silva")
        email = st.text_input("**Email**", placeholder="Ex: ana.silva@email.com")
    with col2:
        telefone = st.text_input("**Telefone**", placeholder="Ex: (11) 99999-8888")

    st.subheader("Formação e experiência")
    formacao = st.text_input("**Formação acadêmica**", placeholder="Ex: Bacharelado em Ciência da Computação - USP")
    experiencia = st.text_area("**Experiência profissional**", height=100,
                               placeholder="Ex: 2 anos como Desenvolvedor Jr na Empresa X...")
    resumo = st.text_area("**Resumo profissional**", height=100,
                          placeholder="Ex: Profissional focado em desenvolvimento backend...")

    st.subheader("Habilidades e certificações")
    #MODIFICADO: usando Text Area para salvar como LISTA
    col_s, col_i, col_c, col_e = st.columns(4)
    with col_s:
        skills_input = st.text_area("**Skills (uma por linha)**", placeholder="Python\nSQL\nGit")
    with col_i:
        idiomas_input = st.text_area("**Idiomas (uma por linha)**", placeholder="Inglês (Avançado)\nEspanhol (Básico)")
    with col_c:
        cert_input = st.text_area("**Certificações (uma por linha)**",
                                  placeholder="AWS Cloud Practitioner\nScrum Master (CSM)")
    with col_e:
        empresas_input = st.text_area("**Empresas prévias (uma por linha)**", placeholder="Empresa X\nStartup Y")

    submitted = st.form_submit_button("Cadastrar currículo")

#Lógica de salvamento, agora com Mongo e Embeddings
if submitted:
    #Validação
    if not all([nome, email, formacao, experiencia, skills_input, idiomas_input, resumo]):
        st.error(
            "⚠️ Por favor, preencha todos os campos obrigatórios (Nome, Email, Formação, Experiência, Skills, Idiomas, Resumo).")
    else:
        try:
            _, col_curriculos, _ = get_collections()
            if col_curriculos is None:
                st.error("Não foi possível conectar à coleção de currículos.")
                st.stop()

            ###########LÓGICA PARA GERAR NOVO ID NUMÉRICO###########
            #Encontra o documento com o 'id' mais alto.
            #Usamos find_one em vez de sort para eficiência
            last_doc = col_curriculos.find_one(sort=[("id", -1)])

            novo_id = 1  #Padrão se a coleção estiver vazia
            if last_doc and "id" in last_doc:
                novo_id = int(last_doc["id"]) + 1
            ########################################################

            #Converte inputs de string (uma por linha) para listas
            skills_list = [s.strip() for s in skills_input.split('\n') if s.strip()]
            idiomas_list = [s.strip() for s in idiomas_input.split('\n') if s.strip()]
            cert_list = [s.strip() for s in cert_input.split('\n') if s.strip()]
            empresas_list = [s.strip() for s in empresas_input.split('\n') if s.strip()]

            #*** USO DE EMBEDDING ***
            st.write("Tentando gerar embedding para o currículo...")
            text_to_embed = (
                f"Formação: {formacao}. Experiência: {experiencia}. "
                f"Resumo: {resumo}. Skills: {', '.join(skills_list)}. "
                f"Idiomas: {', '.join(idiomas_list)}."
            )

            embedding = create_embedding(text_to_embed)

            ########## LÓGICA DE FALHA MODIFICADA (Tolerante) ##########
            embedding_to_save = []  #Define um valor padrão (lista vazia)
            if embedding is None:
                st.warning(
                    "⚠️ AVISO: Falha ao gerar embedding (Quota Excedida?). O currículo será salvo SEM a função de busca por IA.")
            else:
                st.success("Embedding gerado com sucesso!")
                embedding_to_save = embedding
            ############################################################

            #Montar o documento para o MongoDB
            novo_curriculo_doc = {
                "id": novo_id,
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "formacao": formacao,
                "experiencia": experiencia,
                "skills": skills_list,
                "idiomas": idiomas_list,
                "certificacoes": cert_list,
                "resumo": resumo,
                "empresas_previas": empresas_list,
                "embedding": embedding_to_save,  #Salva o vetor (ou lista vazia)
                "data_cadastro": datetime.datetime.now(datetime.timezone.utc)
            }

            #Inserir no banco
            result = col_curriculos.insert_one(novo_curriculo_doc)

            st.success(f"🎉 Currículo de '{nome}' (ID: {novo_id}) cadastrado com sucesso!")
            st.info(f"ID do MongoDB: `{result.inserted_id}`")
            st.balloons()

            #Limpa o cache para a lista ser atualizada automaticamente
            st.cache_data.clear()

        except PyMongoError as e:
            st.error(f"Erro ao salvar no MongoDB: {e}")
        except Exception as e:
            st.error(f"Um erro inesperado ocorreu: {e}")