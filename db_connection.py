import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai
from pymongo.errors import ConnectionFailure

#Nome do banco e coleções
DB_NAME = "Empregos"
COL_VAGAS = "vagas"
COL_CURRICULOS = "curriculos"
COL_USUARIOS = "usuarios"

#--- Conexão ao Google AI Studio ---
@st.cache_resource
def configure_google_ai():
    """
    Configura a API do Google AI.
    """
    try:
        #Pega a chave do secrets.toml
        if "GOOGLE_AI_KEY" in st.secrets:
            google_api_key = st.secrets["GOOGLE_AI_KEY"]
            genai.configure(api_key=google_api_key)
            return True
        else:
            print("❌ Erro: Chave GOOGLE_AI_KEY não encontrada nos secrets.")
            return False
    except Exception as e:
        print(f"❌ Erro ao configurar Google AI: {e}")
        return False


def create_embedding(text_to_embed):
    """
    Gera o embedding (vetor) para o texto.
    Modelo: text-embedding-004 (768 dimensões).
    """
    if not configure_google_ai():
        return None

    try:
        #O modelo text-embedding-004 gera 768 dimensões por padrão.
        #Não definimos output_dimensionality para evitar cortes.
        result = genai.embed_content(
            model='models/text-embedding-004',
            content=text_to_embed,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result['embedding']
    except Exception as e:
        #Retorna None para que o script saiba que falhou (cota ou erro)
        print(f"⚠️ Erro na API do Google: {e}")
        return None

#--- Conexão ao MongoDB Atlas ---
@st.cache_resource
def get_mongo_client():
    """
    Conecta-se ao MongoDB Atlas usando a URI dos segredos.
    Usa @st.cache_resource para manter a conexão viva.
    """
    try:
        mongo_uri = st.secrets["MONGO_URI"]
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        #Testa a conexão
        client.server_info()
        print("Conectado ao MongoDB Atlas com sucesso!")
        return client
    except ConnectionFailure:
        st.error("Falha ao conectar ao MongoDB Atlas. Verifique sua MONGO_URI e o IP Access List.", icon="🚨")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao conectar ao Mongo: {e}")
        return None


def get_db():
    """Retorna a instância do banco de dados 'Empregos'."""
    client = get_mongo_client()
    if client:  #Esta checagem (if client) está OK!
        return client[DB_NAME]
    return None


def get_collections():
    """Retorna as coleções de vagas, currículos e usuários."""
    db = get_db()

    if db is not None:
        return db[COL_VAGAS], db[COL_CURRICULOS], db[COL_USUARIOS]
    return None, None, None