import streamlit as st
from db_connection import get_collections
import bcrypt
import datetime

#DADOS DO ADMIN (mude aqui se quiser)
ADMIN_EMAIL = "emailaqui@example.com"
ADMIN_PASS = "senhaaqui"  #LEMBRETE: Usar uma senha forte na vida real

st.title("🛠️ Script de criação de USUÁRIO ADMINISTRADOR")

if st.button("Criar usuário Admin"):
    _, _, col_usuarios = get_collections()

    if col_usuarios is None:
        st.error("Erro no banco.")
        st.stop()

    #Verifica se já existe
    if col_usuarios.find_one({"email": ADMIN_EMAIL}):
        st.warning(f"O usuário {ADMIN_EMAIL} já existe!")
    else:
        #Cria o documento
        admin_doc = {
            "email": ADMIN_EMAIL,
            "password_hash": bcrypt.hashpw(ADMIN_PASS.encode('utf-8'), bcrypt.gensalt()),
            "tipo_usuario": "admin",
            "data_cadastro": datetime.datetime.now(datetime.timezone.utc),
            #Admin não precisa de empresa nem curriculo
            "empresa": None,
            "id_curriculo": None
        }

        col_usuarios.insert_one(admin_doc)
        st.success(f"Admin criado com sucesso! Login: {ADMIN_EMAIL} / Senha: {ADMIN_PASS}")