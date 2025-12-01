import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai
from pymongo.errors import ConnectionFailure
from typing import Literal

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

# --- Função de Pesquisa RAG (Retrieval) ---
# Vetoriza a consulta do usuário e usa o Atlas Vector Search
def search_rag(
    user_query: str,
    target_collection: Literal["vagas", "curriculos"],
    limit: int = 5
):
    """
    Realiza a busca semântica no MongoDB Atlas.
    """
    vagas_col, curriculos_col, _ = get_collections()

    # Definição dos parâmetros baseados na escolha do usuário
    if target_collection == "vagas":
        collection = vagas_col
        index_name = "vagas_embedding_index" 
        return_fields = {"titulo": 1, "descricao": 1, "empresa": 1, "salario": 1, "skills": 1}
    elif target_collection == "curriculos":
        collection = curriculos_col
        index_name = "curriculos_embedding_index"
        return_fields = {"nome": 1, "resumo": 1, "experiencia": 1, "skills": 1, "formacao": 1}
    else:
        print("Coleção alvo inválida.")
        return []

    # 1. Gerar embedding da pergunta
    query_vector = create_embedding(user_query)
    if query_vector is None:
        return []

    # 2. Pipeline de Agregação (Vector Search)
    # Nota: O campo no banco se chama 'embedding' em ambos os cadastros.
    aggregation_pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": "embedding", 
                "queryVector": query_vector,
                "numCandidates": 100, 
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 1,
                "score": { "$meta": "vectorSearchScore" },
                **return_fields # Desempacota os campos que queremos retornar
            }
        }
    ]

    try:
        results = list(collection.aggregate(aggregation_pipeline))
        print(f"✅ Encontrados {len(results)} documentos similares em '{target_collection}'.")
        return results
    except Exception as e:
        print(f"❌ Erro na Pesquisa Vetorial: {e}")
        return []