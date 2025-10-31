import streamlit as st
import pandas as pd
import os
import streamlit_shadcn_ui as st_shadcn

#Configuração da Página
st.set_page_config(
    page_title="Cadastro de Currículo",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Cadastro de Novo Currículo")
st.write("Preencha o formulário abaixo para adicionar um novo currículo ao sistema.")

#Constantes
CURRICULOS_CSV_PATH = "curriculos.csv"


#Funções Auxiliares
def load_data(filepath, sep=';'):
    """Carrega os dados do CSV. Se o arquivo não existir, cria um DataFrame vazio com as colunas."""
    if os.path.exists(filepath):
        try:
            return pd.read_csv(filepath, sep=sep)
        except pd.errors.EmptyDataError:
            pass

    #Colunas esperadas se o arquivo não existir ou estiver vazio
    columns = [
        'id', 'nome', 'email', 'telefone', 'formacao', 'experiencia',
        'skills', 'idiomas', 'certificacoes', 'resumo',
        'empresas_previas', 'ids_contatos'
    ]
    return pd.DataFrame(columns=columns)


def save_data(df, filepath, sep=';'):
    """Salva o DataFrame no arquivo CSV."""
    df.to_csv(filepath, sep=sep, index=False)


#Carregamento de Dados
df_curriculos = load_data(CURRICULOS_CSV_PATH)

#Formulário de Cadastro
st.markdown("---")

with st.form(key="cadastro_curriculo", clear_on_submit=True):
    st.subheader("Informações Pessoais")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("**Nome Completo**")
        email = st.text_input("**Email**", placeholder="email@exemplo.com")
    with col2:
        telefone = st.text_input("**Telefone**", placeholder="+55 11 9XXXX-XXXX")

    st.subheader("Formação e Experiência")
    col3, col4 = st.columns(2)
    with col3:
        formacao = st.text_input("**Formação Acadêmica**", placeholder="Ex: Bacharelado em Ciência da Computação")
    with col4:
        experiencia = st.text_input("**Experiência**", placeholder="Ex: 5 anos como analista de dados")

    resumo = st.text_area("**Resumo Profissional**", placeholder="Um breve parágrafo sobre sua carreira...")

    st.subheader("Competências")
    col5, col6 = st.columns(2)
    with col5:
        skills = st.text_input("**Skills (separadas por vírgula)**", placeholder="Ex: Python, Pandas, Streamlit")
        idiomas = st.text_input("**Idiomas (separados por vírgula)**", placeholder="Ex: Inglês, Espanhol")
    with col6:
        certificacoes = st.text_input("**Certificações (separadas por vírgula)**",
                                      placeholder="Ex: AWS Certified, Scrum Master")
        empresas_previas = st.text_input("**Empresas Prévias (separadas por vírgula)**",
                                         placeholder="Ex: Google, Microsoft")

    #O campo 'ids_contatos' parece ser relacional/automático, não sei o que fazer ainda
    #Vamos deixá-lo em branco no cadastro manual por enquanto

    submitted = st.form_submit_button("Cadastrar Currículo")

#Lógica de Salvamento
if submitted:
    #Validação básica (ajuste conforme necessidade)
    if not all([nome, email, formacao, experiencia, skills, idiomas]):
        st.error("⚠️ Por favor, preencha pelo menos: Nome, Email, Formação, Experiência, Skills e Idiomas.")
    else:
        try:
            #Gerar novo ID
            if df_curriculos.empty:
                novo_id = 1
            else:
                novo_id = int(df_curriculos['id'].max()) + 1

            #Criar novo registro
            novo_curriculo = pd.DataFrame([{
                'id': novo_id,
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'formacao': formacao,
                'experiencia': experiencia,
                'skills': skills,
                'idiomas': idiomas,
                'certificacoes': certificacoes,
                'resumo': resumo,
                'empresas_previas': empresas_previas,
                'ids_contatos': ""  # Deixando em branco, conforme discutido
            }])

            #Adicionar ao DataFrame principal
            df_atualizado = pd.concat([df_curriculos, novo_curriculo], ignore_index=True)

            #Salvar no CSV
            save_data(df_atualizado, CURRICULOS_CSV_PATH)

            st.success(f"🎉 Currículo de '{nome}' cadastrado com sucesso! (ID: {novo_id})")
            st.balloons()

        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o currículo: {e}")