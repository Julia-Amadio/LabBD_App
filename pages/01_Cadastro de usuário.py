import streamlit as st
from db_connection import get_collections
import re
import bcrypt
from pymongo.errors import PyMongoError
import datetime


#--- Funções auxiliares ---
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


#--- Configuração da página ---
st.set_page_config(page_title="Cadastro de Usuário", page_icon="📝", layout="centered")

st.title("📝 Criar Nova Conta")
st.write("Crie sua conta para acessar o sistema.")

#--- Seleção de perfil (FORA DO FORMULÁRIO) ---
#Ao colocar fora, o Streamlit recarrega a página assim que você muda a opção,
#permitindo esconder/mostrar campos dinamicamente.
#Estamos usando isso para ESCONDER o campo EMPRESA ao cadastrar um CANDIDATO.
tipo_selecionado = st.radio(
    "Eu sou um:",
    ["Candidato", "Empregador"],
    horizontal=True,
    help="Selecione seu perfil para ver os campos adequados."
)

st.markdown("---")

with st.form(key="register_form", clear_on_submit=True):
    #1. Dados de login
    email = st.text_input("Email", placeholder="email@exemplo.com")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirme a Senha", type="password")

    #2. Campo condicional (só aparece se for empregador)
    empresa_nome = ""  #Inicializa vazio para não quebrar a lógica se for candidato

    if tipo_selecionado == "Empregador":
        st.markdown("### Informações da Empresa")
        empresa_nome = st.text_input(
            "Nome da Empresa",
            placeholder="Ex: Microsoft Brasil",
            help="Obrigatório para contas empresariais (EMPREGADOR)."
        )

    submit_button = st.form_submit_button("Cadastrar")

if submit_button:
    _, _, col_usuarios = get_collections()

    if col_usuarios is None:
        st.error("Erro de conexão com o banco.")
        st.stop()

    #--- Validações ---
    if not is_valid_email(email):
        st.error("Email inválido.")
        st.stop()

    if password != confirm_password:
        st.error("As senhas não coincidem.")
        st.stop()

    if len(password) < 6:
        st.error("Senha muito curta (mínimo 6 caracteres).")
        st.stop()

    #Validação de negócio
    tipo_tecnico = tipo_selecionado.lower()  #"candidato" ou "empregador"

    if tipo_tecnico == "empregador" and not empresa_nome:
        st.error("⚠️ Empregadores precisam informar o nome da empresa.")
        st.stop()

    #Verifica duplicidade
    if col_usuarios.find_one({"email": email}):
        st.error("Este email já está cadastrado.")
        st.stop()

    #--- Montagem do documento ---
    try:
        novo_usuario = {
            "email": email,
            "password_hash": hash_password(password),
            "tipo_usuario": tipo_tecnico,
            "data_cadastro": datetime.datetime.now(datetime.timezone.utc),

            #Lógica condicional de campos
            "empresa": empresa_nome if tipo_tecnico == "empregador" else None,
            "id_curriculo": None  #Inicializa vazio para todos
        }

        col_usuarios.insert_one(novo_usuario)

        st.success(f"Conta de {tipo_selecionado} criada com sucesso!")
        st.info("Vá para a página de **Login** para entrar.")

    except Exception as e:
        st.error(f"Erro ao salvar: {e}")