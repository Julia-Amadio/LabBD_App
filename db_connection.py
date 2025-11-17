import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai
from pymongo.errors import ConnectionFailure

#Nome do Banco e Coleções
DB_NAME = "Empregos"
COL_VAGAS = "vagas"
COL_CURRICULOS = "curriculos"
COL_USUARIOS = "usuarios"


#Conexão ao Google AI para Embeddings

@st.cache_resource
def configure_google_ai():
    """
    Configura a API do Google AI.
    Retorna True se for bem-sucedido, False caso contrário.
    """
    try:
        google_api_key = st.secrets["GOOGLE_AI_KEY"]
        genai.configure(api_key=google_api_key)
        print("Google AI configurado com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao configurar o Google AI Studio: {e}")
        return False


def create_embedding(text_to_embed):
    """
    Cria um embedding para um dado texto.
    Retorna o vetor (lista de floats) ou None se falhar.
    """
    #Garante que a API está configurada
    if not configure_google_ai():
        st.warning("API do Google AI não configurada.")
        return None

    try:
        #Passamos o NOME DO MODELO (string) e não um objeto GenerativeModel
        result = genai.embed_content(
            model='models/embedding-001',
            content=text_to_embed,
            task_type="RETRIEVAL_DOCUMENT"  #Otimizado para busca
        )
        return result['embedding']
    except Exception as e:
        st.warning(f"Não foi possível gerar o embedding: {e}")
    return None


#Conexão ao MongoDB Atlas

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