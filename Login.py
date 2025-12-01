import streamlit as st
import pandas as pd
from db_connection import get_collections
import bcrypt

st.set_page_config(
    page_title="Login - App de vagas",
    page_icon="🔑",
    layout="centered"
)

#--- Inicialização da sessão ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['email'] = ""
    st.session_state['tipo_usuario'] = ""
    st.session_state['empresa'] = None
    st.session_state['id_curriculo'] = None


#--- Funções de autenticação ---
def login_user(email, password):
    """
    Verifica credenciais e retorna os dados do usuário se válido.
    """
    _, _, col_usuarios = get_collections()
    if col_usuarios is None:
        st.error("Erro de conexão com o banco.")
        return None

    #Busca o usuário pelo email
    user_data = col_usuarios.find_one({"email": email})

    if user_data:
        #Verifica a senha (bcrypt lida com o formato Binary do MongoDB automaticamente)
        stored_hash = user_data['password_hash']
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return user_data

    return None


def logout():
    """Limpa toda a sessão."""
    st.session_state.clear()
    st.rerun()


#--- Interface ---
if st.session_state['logged_in']:
    #Sidebar com informações do usuário logado
    st.sidebar.write(f"👤 **{st.session_state['email']}**")
    st.sidebar.caption(f"Perfil: {st.session_state['tipo_usuario'].upper()}")

    if st.sidebar.button("Sair / Logout"):
        logout()

    st.title("Bem-vindo ao sistema! 🚀")

    #Mensagem personalizada por tipo
    tipo = st.session_state['tipo_usuario']
    if tipo == 'empregador':
        empresa = st.session_state.get('empresa', 'Sua empresa')
        st.success(f"Você está logado em sua conta corporativa da empresa **{empresa}**")
        st.write("Utilize o menu lateral para **Cadastrar vagas** ou **Listar currículos**.")

    elif tipo == 'candidato':
        st.info("Você está logado como **Candidato**.")
        if st.session_state['id_curriculo']:
            st.write("✅ Você já possui um currículo cadastrado.")
        else:
            st.warning("⚠️ Você ainda não cadastrou seu currículo. Vá em **Cadastrar currículo** para começar.")

    elif tipo == 'admin':
        st.error("🔧 **Modo ADMIN ativado!**")
        st.write("Você tem acesso irrestrito a **todas** as funções.")

else:
    st.title("Login do sistema 🔑")
    st.write("Entre com suas credenciais para acessar.")

    with st.form(key="login_form"):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        user = login_user(email, password)
        if user:
            #SUCESSO: salva dados cruciais na sessão
            st.session_state['logged_in'] = True
            st.session_state['email'] = user['email']
            st.session_state['tipo_usuario'] = user['tipo_usuario']

            #Recupera dados opcionais com segurança (.get)
            st.session_state['empresa'] = user.get('empresa')
            st.session_state['id_curriculo'] = user.get('id_curriculo')

            st.rerun()
        else:
            st.error("Email ou senha incorretos.")