import streamlit as st
from db_connection import get_collections, create_embedding
from pymongo.errors import PyMongoError
import datetime

#------- CONTROLE DE ACESSO -------
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Por favor, faça login.")
    st.stop()

tipo_usuario = st.session_state['tipo_usuario']
id_curriculo_usuario = st.session_state.get('id_curriculo') #Pode ser None

#Regra 1: empregador fora
if tipo_usuario == 'empregador':
    st.error("⛔ ACESSO RESTRITO: empregadores não podem cadastrar currículos!")
    st.stop()

#Regra 2: candidato que JÁ TEM currículo -> Modo misualização
modo_visualizacao = False
curriculo_existente = None

if tipo_usuario == 'candidato' and id_curriculo_usuario is not None:
    modo_visualizacao = True
    #Busca os dados dele para mostrar
    _, col_curriculos, _ = get_collections()

    if col_curriculos is not None:  #Verifica explicitamente por None
        curriculo_existente = col_curriculos.find_one({"id": id_curriculo_usuario})
#----------------------------------

st.set_page_config(page_title="Meu currículo", page_icon="👤", layout="wide")

if modo_visualizacao:
    #--- TELA DE VISUALIZAÇÃO (READ-ONLY) ---
    st.title("👤 Meu currículo")
    st.info("Você já possui um currículo ativo no sistema!")

    if curriculo_existente:
        c = curriculo_existente

        #Cabeçalho principal
        st.markdown("---")
        st.header(c.get('nome', 'Sem Nome'))
        st.caption(f"ID Interno: {c.get('id')} | Cadastrado em: {c.get('data_cadastro', 'Data N/A')}")
        st.markdown("")  #Espaço extra

        #--- LAYOUT MELHORADO (BLOCOS E ESPAÇAMENTO) ---
        #Criamos 3 colunas: [Conteúdo 1] [Espaço vazio] [Conteúdo 2]
        #A proporção [1, 0.1, 1] cria um pequeno gap no meio
        col_resumo, gap, col_detalhes = st.columns([1, 0.1, 1])

        #BLOCO DA ESQUERDA (resumo e formação)
        with col_resumo:
            with st.container(border=True):  #Cria a borda do "card"
                st.subheader("🎓 Formação & Resumo")
                st.markdown(f"**Formação:** {c.get('formacao', '')}")

                st.markdown("### Resumo Profissional")
                st.info(c.get('resumo', 'Sem resumo.'))

                st.markdown("### Experiência")
                st.write(c.get('experiencia', 'Não informada.'))

        #BLOCO DA DIREITA (contato e skills)
        with col_detalhes:
            with st.container(border=True):  #Cria a borda do "card"
                st.subheader("📞 Contatos")

                st.markdown(f"**📧 Email:** {c.get('email')}")
                st.markdown(f"**📞 Telefone:** {c.get('telefone')}")

                st.divider()  #Linha divisória visual

                st.markdown("### Competências")
                #Helper para exibir listas bonitas
                def show_list(label, items):
                    if items and isinstance(items, list) and len(items) > 0 and items[0] != "":
                        #Exibe como tags (code block inline) para ficar bonito e separado
                        tags = " ".join([f"`{item}`" for item in items])
                        st.markdown(f"**{label}:** {tags}")


                show_list("🛠 Skills", c.get('skills', []))
                show_list("🗣 Idiomas", c.get('idiomas', []))
                show_list("🏅 Certificações", c.get('certificacoes', []))

    else:
        st.error("Erro: Seu ID consta no usuário, mas o currículo não foi achado. Contate o suporte.")

    st.stop()  #Para aqui, não mostra o formulário de cadastro

#--- TELA DE CADASTRO (admin ou candidato novo) ---
st.title("👤 Cadastro de novo currículo")
st.write("Preencha o formulário abaixo.")

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
            _, col_curriculos, col_usuarios = get_collections()
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
            #1. Insere Currículo
            col_curriculos.insert_one(novo_curriculo_doc)

            #2. VINCULA AO USUÁRIO (se for candidato)
            if tipo_usuario == 'candidato':
                col_usuarios.update_one(
                    {"email": st.session_state['email']},
                    {"$set": {"id_curriculo": novo_id}}
                )
                #Atualiza a sessão local também para não precisar relogar
                st.session_state['id_curriculo'] = novo_id

            st.success(f"🎉 Currículo cadastrado! ID: {novo_id}")
            st.balloons()
            st.rerun()  #Recarrega para mostrar a tela de visualização

        except PyMongoError as e:
            st.error(f"Erro ao salvar no MongoDB: {e}")
        except Exception as e:
            st.error(f"Um erro inesperado ocorreu: {e}")