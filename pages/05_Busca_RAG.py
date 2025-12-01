import streamlit as st
from db_connection import search_rag

st.set_page_config(page_title="Busca Inteligente (IA)", page_icon="🤖", layout="wide")

st.title("🤖 Busca Inteligente com IA")
st.markdown("""
Diferente da busca tradicional por palavras-chave, aqui você pode descrever o que procura.
O sistema entenderá o **contexto** e o **significado** da sua busca (Busca Semântica).
""")

# --- Radio Button ---
tipo_busca = st.radio(
    "O que você deseja buscar?",
    ["Vagas", "Currículos"],
    horizontal=True,
    help="Selecione 'Vagas' se você é um candidato, ou 'Currículos' se você é uma empresa."
)

target_collection = "vagas" if tipo_busca == "Vagas" else "curriculos"

# --- Campo de Busca ---
user_query = st.text_input(
    "Descreva o que você procura:",
    placeholder="Ex: Procuro um especialista em dados que saiba Python e tenha experiência com bancos não relacionais." 
                if tipo_busca == "Currículos" 
                else "Ex: Vagas para desenvolvedor junior home office com foco em frontend."
)

st.markdown("---")

if user_query:
    with st.spinner(f"A IA está analisando sua busca na base de {tipo_busca}..."):
        resultados = search_rag(user_query, target_collection, limit=6)

    if not resultados:
        st.warning("Nenhum resultado relevante encontrado para essa descrição.")
    else:
        st.success(f"Encontramos {len(resultados)} correspondências baseadas no significado!")
        
        # Exibição dos Cards
        for doc in resultados:
            score = doc.get('score', 0)
            score_percent = f"{score * 100:.1f}%"
            
            if target_collection == "vagas":
                # Layout para Vagas
                with st.expander(f"{doc.get('titulo', 'Sem título')} | {doc.get('empresa', 'N/A')} ({score_percent} match)"):
                    st.markdown(f"**Descrição:** {doc.get('descricao')}")
                    st.markdown(f"**Skills:** {', '.join(doc.get('skills', []))}")
                    if doc.get('salario'):
                        st.markdown(f"**Salário:** R$ {doc.get('salario'):.2f}")
                        
            else:
                # Layout para Currículos
                with st.expander(f"{doc.get('nome', 'Candidato')} | {doc.get('formacao', 'N/A')} ({score_percent} match)"):
                    st.markdown(f"**Resumo:** {doc.get('resumo')}")
                    st.markdown(f"**Experiência:** {doc.get('experiencia')}")
                    st.markdown(f"**Skills:** {', '.join(doc.get('skills', []))}")