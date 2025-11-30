import streamlit as st
from db_connection import get_collections, create_embedding
from pymongo.errors import PyMongoError
import datetime

#Configuração da página
st.set_page_config(
    page_title="Cadastro de currículos",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Cadastro de novo currículo")
st.write("Preencha o formulário abaixo para adicionar um novo currículo ao banco de dados.")

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
    st.caption("💡 Para listas, digite um item e pressione ENTER para pular para a próxima linha.")

    col_s, col_i, col_c, col_e = st.columns(4)
    with col_s:
        skills_input = st.text_area("**Skills**", placeholder="Python\nSQL\nGit",
                                    help="Digite uma habilidade por linha.")
    with col_i:
        idiomas_input = st.text_area("**Idiomas**", placeholder="Inglês (Avançado)\nEspanhol (Básico)",
                                     help="Digite um idioma por linha.")
    with col_c:
        cert_input = st.text_area("**Certificações**", placeholder="AWS Cloud Practitioner\nScrum Master",
                                  help="Digite uma certificação por linha.")
    with col_e:
        empresas_input = st.text_area("**Empresas prévias**", placeholder="Empresa X\nStartup Y",
                                      help="Digite uma empresa por linha.")

    submitted = st.form_submit_button("Cadastrar currículo")

#Lógica de salvamento
if submitted:
    #Validação
    if not all([nome, email, formacao, experiencia, skills_input, idiomas_input, resumo]):
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
    else:
        try:
            _, col_curriculos, _ = get_collections()
            if col_curriculos is None:
                st.error("Não foi possível conectar à coleção de currículos.")
                st.stop()

            #Lógica para gerar ID sequencial
            last_doc = col_curriculos.find_one(sort=[("id", -1)])
            novo_id = 1
            if last_doc and "id" in last_doc:
                novo_id = int(last_doc["id"]) + 1

            #Converte inputs de string para listas
            skills_list = [s.strip() for s in skills_input.split('\n') if s.strip()]
            idiomas_list = [s.strip() for s in idiomas_input.split('\n') if s.strip()]
            cert_list = [s.strip() for s in cert_input.split('\n') if s.strip()]
            empresas_list = [s.strip() for s in empresas_input.split('\n') if s.strip()]

            #---------- GERAÇÃO DE EMBEDDING ----------
            embedding_to_save = []
            st.info("Gerando embedding para o currículo...")
            text_to_embed = (
                f"Formação: {formacao}. Experiência: {experiencia}. "
                f"Resumo: {resumo}. Skills: {', '.join(skills_list)}. "
                f"Idiomas: {', '.join(idiomas_list)}."
            )

            embedding = create_embedding(text_to_embed)
            if embedding:
                embedding_to_save = embedding
                st.success("✨ Embedding gerado com sucesso!")
            else:
                st.warning("⚠️ Cota do Google AI Studio excedida. O registro foi salvo no banco sem embedding.")
            #-----------------------------------------

            #Montar o documento (direto, sem lógica de IA)
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
                "embedding": embedding_to_save, #Salva o vetor ou lista vazia
                "data_cadastro": datetime.datetime.now(datetime.timezone.utc)
            }

            #Inserir no banco
            result = col_curriculos.insert_one(novo_curriculo_doc)

            st.success(f"🎉 Currículo de '{nome}' (ID: {novo_id}) cadastrado com sucesso!")
            st.info(f"ID do MongoDB: `{result.inserted_id}`")
            st.balloons()

            st.cache_data.clear()

        except PyMongoError as e:
            st.error(f"Erro ao salvar no MongoDB: {e}")
        except Exception as e:
            st.error(f"Um erro inesperado ocorreu: {e}")