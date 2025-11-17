import streamlit as st
from db_connection import get_collections  #Importa nossa nova função
import re
import bcrypt  #Usaremos bcrypt para senhas
from pymongo.errors import PyMongoError


#Funções de usuário (agora com Mongo)

def is_valid_email(email):
    """Valida o formato do email usando regex."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)


def hash_password(password):
    """Gera um hash seguro para a senha."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


#Configuração da página
st.set_page_config(
    page_title="Cadastro de Usuário",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Cadastro de Novo Usuário (MongoDB)")
st.warning("As senhas são agora armazenadas com hash de segurança (bcrypt).", icon="🔒")

with st.form(key="register_form", clear_on_submit=True):
    email = st.text_input("Email", placeholder="email@exemplo.com")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirme a Senha", type="password")

    submit_button = st.form_submit_button("Cadastrar")

if submit_button:
    _, _, col_usuarios = get_collections()
    if col_usuarios is None:
        st.error("Não foi possível conectar ao banco de dados de usuários.")
        st.stop()

    #Verifica se o usuário já existe
    existing_user = col_usuarios.find_one({"email": email})

    #Validações
    if not is_valid_email(email):
        st.error("Por favor, insira um email válido.")
    elif password != confirm_password:
        st.error("As senhas não coincidem.")
    elif len(password) < 8:
        st.error("A senha deve ter pelo menos 8 caracteres.")
    elif existing_user:
        st.error("Este email já está cadastrado.")
    else:
        #Sucesso
        try:
            #Gera o hash da senha
            password_hash = hash_password(password)

            #Cria o novo documento de usuario
            novo_usuario_doc = {
                "email": email,
                "password_hash": password_hash,  #Salva o hash, não a senha
                "tipo_usuario": "candidato"  #Define um tipo padrão
            }

            #Insere no MongoDB
            result = col_usuarios.insert_one(novo_usuario_doc)

            st.success(f"Usuário '{email}' cadastrado com sucesso!")
            st.info(f"ID do Usuário: {result.inserted_id}")

        except PyMongoError as e:
            st.error(f"Erro ao salvar no MongoDB: {e}")
        except Exception as e:
            st.error(f"Um erro inesperado ocorreu: {e}")