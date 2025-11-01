import streamlit as st
import pandas as pd
import os

with st.sidebar:
    st.image("https://www2.unesp.br/images/unesp-full-center.svg")

#Configuração da Página
st.set_page_config(
    page_title="Login - App de Vagas",
    page_icon="🔑",
    layout="centered"
)

#Constantes
USUARIOS_CSV_PATH = "usuarios.csv"
USUARIOS_COLUMNS = ['email', 'password']  #Armazenaremos a senha em texto puro

#Funções de Usuário
def load_users():
    """Carrega o CSV de usuários. Se não existir, cria um DataFrame vazio."""
    if not os.path.exists(USUARIOS_CSV_PATH):
        return pd.DataFrame(columns=USUARIOS_COLUMNS)
    try:
        return pd.read_csv(USUARIOS_CSV_PATH, sep=';')
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=USUARIOS_COLUMNS)

def check_login(email, password):
    """Verifica as credenciais (email e senha em texto puro)."""
    df_users = load_users()
    if df_users.empty:
        return False

    #Filtra pelo email
    user_data = df_users[df_users['email'] == email]

    if user_data.empty:
        return False

    #Compara a senha em texto puro
    return user_data.iloc[0]['password'] == password

#Função de Logout
def logout():
    """Limpa o estado da sessão."""
    st.session_state['logged_in'] = False
    st.session_state['email'] = ""
    st.rerun()

#Inicialização do Estado da Sessão
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['email'] = ""

#-------------------------------Lógica da Interface

#Se o usuário JÁ ESTIVER LOGADO
if st.session_state['logged_in']:
    st.sidebar.success(f"Logado como: {st.session_state['email']}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("Bem-vindo ao Sistema! 🚀")
    st.write("Navegue pelas páginas na barra lateral para cadastrar ou visualizar vagas e currículos.")
    st.info("Você já está logado. Para sair, clique no botão 'Logout' na barra lateral.")

#Se o usuário NÃO ESTIVER LOGADO
else:
    st.title("Login do Sistema 🔑")
    st.write("Por favor, insira suas credenciais para acessar.")

    with st.form(key="login_form"):
        email = st.text_input("Email", placeholder="email@exemplo.com")
        password = st.text_input("Senha", type="password")

        submit_button = st.form_submit_button("Entrar")

    if submit_button:
        if check_login(email, password):
            st.session_state['logged_in'] = True
            st.session_state['email'] = email
            st.success("Login realizado com sucesso!")
            st.rerun()  #Recarrega a página para mostrar o estado logado
        else:
            st.error("Email ou senha incorretos. Tente novamente.")

    st.info("Não tem uma conta? Utilize a página 'Cadastro de Usuário' na barra lateral!")