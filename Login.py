import streamlit as st
import pandas as pd
from db_connection import get_collections  #Importa nossa nova função
import bcrypt  #Usaremos bcrypt para senhas (muito mais seguro)

with st.sidebar:
    st.image("https://www2.unesp.br/images/unesp-full-center.svg")

st.set_page_config(
    page_title="Login - App de Vagas",
    page_icon="🔑",
    layout="centered"
)


#Funções de usuário, agora com MongoDB

def check_login(email, password):
    """Verifica as credenciais contra o MongoDB."""
    _, _, col_usuarios = get_collections()
    if col_usuarios is None:
        st.error("Não foi possível conectar ao banco de dados de usuários.")
        return False

    user_data = col_usuarios.find_one({"email": email})

    if user_data:
        #Verifica a senha hasheada
        if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash']):
            return True

    return False


def logout():
    """Limpa o estado da sessão ao fazer logout."""
    st.session_state['logged_in'] = False
    st.session_state['email'] = ""
    st.success("Logout realizado com sucesso!")
    st.rerun()


#Estado da sessão (sem mudanças)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['email'] = ""

#Lógica da interface

if st.session_state['logged_in']:
    st.sidebar.success(f"Logado como: {st.session_state['email']}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("Bem-vindo ao Sistema! 🚀")
    st.write("Navegue pelas páginas na barra lateral para cadastrar ou visualizar vagas e currículos.")
    st.info("Você já está logado. Para sair, clique no botão 'Logout' na barra lateral.")

else:
    st.title("Login do Sistema 🔑")
    st.write("Por favor, insira suas credenciais para acessar.")
    st.info("Esta é uma simulação. O cadastro de usuários também foi movido para o MongoDB.", icon="ℹ️")

    with st.form(key="login_form"):
        email = st.text_input("Email", placeholder="email@exemplo.com")
        password = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Entrar")

    if submit_button:
        if check_login(email, password):
            st.session_state['logged_in'] = True
            st.session_state['email'] = email
            st.rerun()
        else:
            st.error("Email ou senha inválidos.")