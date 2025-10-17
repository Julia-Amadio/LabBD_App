import streamlit as st

st.write("Olá mundo!")

st.title("Cadastro de usuários:")

with st.sidebar: 
    st.image("https://www2.unesp.br/images/unesp-full-center.svg")
    st.title("Configurações")


with st.form("form_usuario"):
    nome = st.text_input("Nome: ")
    senha = st.text_input("Senha: ", type="password")
    numero = st.slider("Escolha um número:", 1, 10)
    cor = st.selectbox("Selecione uma cor:", ["Vermelho", "Amarelo", "Azul"])
    submit = st.form_submit_button("Enviar")

st.write(st.secrets["db_name"])

def validar(nome, senha):
    if nome =="" or senha=="":
        return False
    return True

if submit and validar(nome, senha):
    #cadastra_usuario(nome, senha) ------------não tá implementando ainda.
    st.write("Dados ok.")
    st.success("Dados inseridos com sucesso!")
elif submit:
    st.warning("Dados inválidos!")