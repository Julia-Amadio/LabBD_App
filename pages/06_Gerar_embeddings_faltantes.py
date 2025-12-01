import time
import datetime
import streamlit as st
import traceback  #Para ver o erro real
from db_connection import get_collections, create_embedding

#--- CONTROLE DE ACESSO (ADMIN ONLY) ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Faça login.")
    st.stop()

if st.session_state['tipo_usuario'] != 'admin':
    st.error("⛔ ACESSO RESTRITO: apenas ADMINISTRADORES podem acessar ferramentas de sistema.")
    st.stop()
#---------------------------------------

st.set_page_config(page_title="Gerador de Embeddings", page_icon="⚙️", layout="wide")

st.title("⚙️ Gerador de Embeddings (backfill)")
st.markdown("Este script processa registros antigos que não possuem o campo `embedding`, ou em que o campo se encontra vazio.")

#Area de logs na tela
log_area = st.empty()
logs_history = []


def log_ui(msg, tipo="info"):
    """Envia logs para a tela do Streamlit e terminal."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{now}] {msg}"

    #Imprime também no terminal para melhor monitoramento
    print(formatted_msg)

    #Adiciona na tela do navegador
    if tipo == "info":
        st.toast(msg, icon="ℹ️")
    elif tipo == "success":
        st.toast(msg, icon="✅")
    elif tipo == "error":
        st.error(formatted_msg)
    elif tipo == "warning":
        st.warning(formatted_msg)

    logs_history.append(formatted_msg)
    #Mostra últimos 5 logs na tela principal
    log_area.code("\n".join(logs_history[-10:]), language="text")


def processar_colecao_visual(nome, collection, campos_texto):
    st.subheader(f"📂 Processando coleção: {nome}")

    #CORREÇÃO AQUI ---
    #Busca pendentes: onde não existe OU onde é uma lista vazia []
    query = {"$or": [{"embedding": {"$exists": False}}, {"embedding": []}]}

    pendentes = list(collection.find(query).sort("id", 1))
    total = len(pendentes)

    if total == 0:
        st.success(f"✅ Coleção {nome} já está 100% atualizada!")
        return

    #Barra de progresso
    progress_bar = st.progress(0, text=f"Iniciando {total} registros...")
    status_text = st.empty()

    for i, doc in enumerate(pendentes):
        doc_id = doc.get('id', 'N/A')
        titulo = doc.get('titulo') or doc.get('nome') or 'Sem Título'

        status_msg = f"Processando item {i + 1}/{total}: ID {doc_id} - {titulo}"
        status_text.text(status_msg)
        progress_bar.progress((i) / total, text=status_msg)

        #Montar texto
        partes = []
        for campo in campos_texto:
            valor = doc.get(campo, "")
            if isinstance(valor, list):
                valor = ", ".join(valor)
            partes.append(f"{str(campo).capitalize()}: {valor}")
        texto_final = ". ".join(partes)

        #Retry loop
        tentativas = 0
        while True:
            vector = create_embedding(texto_final)

            if vector:
                #SUCESSO
                collection.update_one({"_id": doc["_id"]}, {"$set": {"embedding": vector}})
                log_ui(f"ID {doc_id}: Salvo com sucesso.", "success")
                time.sleep(10)  #Pausa de segurança para não exceder limite de requests/min (Free Tier)
                break
            else:
                #FALHA
                tentativas += 1
                if tentativas == 1:
                    wait = 60
                elif tentativas <= 3:
                    wait = 300
                else:
                    wait = 3600

                log_ui(f"Falha ao gerar ID {doc_id}. Tentativa {tentativas}. Esperando {wait}s...", "warning")

                #Countdown visual
                for s in range(wait, 0, -1):
                    status_text.text(f"⏳ Cota excedida. Dormindo... {s}s restantes.")
                    time.sleep(1)

                status_text.text("🔄 Tentando novamente...")

    progress_bar.progress(1.0, text="Concluído!")
    st.success(f"Coleção {nome} finalizada!")


def main():
    if st.button("▶️ Iniciar processamento"):
        try:
            col_vagas, col_curriculos, _ = get_collections()

            #Trocamos "if not col_vagas:" por "if col_vagas is None:"
            if col_vagas is None:
                st.error("Erro crítico: Não conectou ao MongoDB.")
                return

            #Vagas
            campos_vaga = ['titulo', 'descricao', 'skills', 'empresa', 'tipo_contratacao']
            processar_colecao_visual("VAGAS", col_vagas, campos_vaga)

            #Currículos
            campos_curriculo = ['formacao', 'experiencia', 'resumo', 'skills', 'idiomas']
            processar_colecao_visual("CURRÍCULOS", col_curriculos, campos_curriculo)

            st.balloons()
            st.success("Progresso completo. Todos os dados agora possuem embeddings.")

        except Exception as e:
            st.error("Ocorreu um erro fatal no script:")
            st.code(traceback.format_exc())  #Mostra o erro real na tela

if __name__ == "__main__":
    main()