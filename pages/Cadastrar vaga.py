import streamlit as st
import pandas as pd
import os

#Configuração da página
st.set_page_config(
    page_title="Cadastro de Vagas",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Cadastro de Nova Vaga")
st.write("Preencha o formulário abaixo para adicionar uma nova vaga ao sistema.")

#Constantes
VAGAS_CSV_PATH = "vagas.csv"


#Funções Auxiliares
def load_data(filepath, sep=';'):
    """Carrega os dados do CSV. Se o arquivo não existir, cria um DataFrame vazio com as colunas."""
    if os.path.exists(filepath):
        try:
            return pd.read_csv(filepath, sep=sep)
        except pd.errors.EmptyDataError:
            # Se o arquivo estiver vazio, mas existir
            pass

    #Colunas esperadas se o arquivo não existir ou estiver vazio
    columns = [
        'id', 'titulo', 'descricao', 'cidade', 'estado',
        'tipo_contratacao', 'salario', 'empresa', 'skills'
    ]
    return pd.DataFrame(columns=columns)


def save_data(df, filepath, sep=';'):
    """Salva o DataFrame no arquivo CSV."""
    df.to_csv(filepath, sep=sep, index=False)


#Carregamento de Dados
df_vagas = load_data(VAGAS_CSV_PATH)

#Formulário de Cadastro
st.markdown("---")
st.subheader("Informações da Vaga")

with st.form(key="cadastro_vaga", clear_on_submit=True):
    #Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        titulo = st.text_input("**Título da Vaga**", placeholder="Ex: Engenheiro de Dados Pleno")
        empresa = st.text_input("**Nome da Empresa**", placeholder="Ex: Inovatech Soluções")
        tipo_contratacao = st.selectbox(
            "**Tipo de Contratação**",
            ["CLT", "PJ", "Estágio", "Temporário"],
            index=None
        )

    with col2:
        #Formatando o salário para o formato do CSV (string com vírgula)
        salario_num = st.number_input("**Salário (R$)**", min_value=0.0, format="%.2f", step=100.0)
        #Convertendo para o formato string '12.345,00'
        salario = f"{salario_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        skills = st.text_input("**Skills (separadas por vírgula)**", placeholder="Ex: Python, SQL, Power BI")

    descricao = st.text_area("**Descrição da Vaga**", placeholder="Descreva as responsabilidades, requisitos...")

    st.subheader("Localização")
    col_loc1, col_loc2 = st.columns([2, 1])

    with col_loc1:
        cidade = st.text_input("**Cidade**", placeholder="Ex: São Paulo")
    with col_loc2:
        estado = st.text_input("**Estado (UF)**", max_chars=2, placeholder="Ex: SP")

    #Botão de Envio
    submitted = st.form_submit_button("Cadastrar Vaga")

#Lógica de Salvamento
if submitted:
    # Validação básica
    if not all([titulo, empresa, tipo_contratacao, skills, cidade, estado, descricao]):
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
    else:
        try:
            #Gerar novo ID
            if df_vagas.empty:
                novo_id = 1
            else:
                novo_id = int(df_vagas['id'].max()) + 1

            #Criar novo registro
            nova_vaga = pd.DataFrame([{
                'id': novo_id,
                'titulo': titulo,
                'descricao': descricao,
                'cidade': cidade,
                'estado': estado.upper(),
                'tipo_contratacao': tipo_contratacao,
                'salario': f" {salario} ",  # Adiciona espaços como no seu CSV
                'empresa': empresa,
                'skills': skills
            }])

            #Adicionar ao DataFrame principal
            df_atualizado = pd.concat([df_vagas, nova_vaga], ignore_index=True)

            #Salvar no CSV
            save_data(df_atualizado, VAGAS_CSV_PATH)

            st.success(f"🎉 Vaga '{titulo}' cadastrada com sucesso! (ID: {novo_id})")
            st.balloons()

        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar a vaga: {e}")