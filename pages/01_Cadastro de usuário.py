import streamlit as st
import pandas as pd
import os
import re  #Para validar email

#Constantes
USUARIOS_CSV_PATH = "usuarios.csv"
USUARIOS_COLUMNS = ['email', 'password']


#Funções de Usuário
def load_users():
    """Carrega o CSV de usuários. Se não existir, cria um DataFrame vazio."""
    if not os.path.exists(USUARIOS_CSV_PATH):
        #Se o arquivo não existe, já retorna o DataFrame vazio
        return pd.DataFrame(columns=USUARIOS_COLUMNS)
    try:
        df = pd.read_csv(USUARIOS_CSV_PATH, sep=';')
        if df.empty:
            return pd.DataFrame(columns=USUARIOS_COLUMNS)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=USUARIOS_COLUMNS)


def save_users(df):
    """Salva o DataFrame de usuários no CSV."""
    #O 'header=True' garante que o cabeçalho seja escrito na primeira vez
    df.to_csv(USUARIOS_CSV_PATH, sep=';', index=False, header=True)


def is_valid_email(email):
    """Valida o formato do email usando regex."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)


#Configuração da Página
st.set_page_config(
    page_title="Cadastro de Usuário",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Cadastro de Novo Usuário")

with st.form(key="register_form", clear_on_submit=True):
    email = st.text_input("Email", placeholder="email@exemplo.com")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirme a Senha", type="password")

    submit_button = st.form_submit_button("Cadastrar")

if submit_button:
    df_users = load_users()

    #Validações
    if not is_valid_email(email):
        st.error("Por favor, insira um email válido.")
    elif password != confirm_password:
        st.error("As senhas não coincidem.")
    elif not df_users.empty and email in df_users['email'].values:
        st.error("Este email já está cadastrado.")
    else:
        #Sucesso
        try:
            #Salva a senha em texto puro
            novo_usuario = pd.DataFrame([[email, password]], columns=USUARIOS_COLUMNS)

            df_atualizado = pd.concat([df_users, novo_usuario], ignore_index=True)

            save_users(df_atualizado)

            st.success("Usuário cadastrado com sucesso! 🥳")
            st.info("Retorne à página de Login para entrar no sistema.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o cadastro: {e}")