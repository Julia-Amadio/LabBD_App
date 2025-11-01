## LabBD_App: Sistema de Gerenciamento de Vagas e Currículos

Este repositório contém o código-fonte de um aplicativo web para gerenciamento de vagas de emprego e currículos, desenvolvido como projeto para a disciplina de Laboratório de Banco de Dados. A aplicação é construída em Python usando a biblioteca Streamlit.

⚠️ **Atenção**: Este projeto está em desenvolvimento. Atualmente, ele utiliza arquivos CSV (vagas.csv, curriculos.csv, usuarios.csv) como um "banco de dados" local para fins de prototipação e teste da interface.

Os dados cadastrados em um ambiente de deploy (como o Streamlit Community Cloud) são efêmeros e serão perdidos sempre que a aplicação "dormir" ou for reiniciada. A próxima etapa do projeto é conectar este frontend a um banco de dados persistente (MySQL, MongoDB, Neo4j).

## 🌐 Deploy do projeto
O deploy foi feito por meio da Streamlit Community Cloud. Este projeto está hospedado na URL https://fakelinkedinlabbd.streamlit.app/.

## ✨ Funcionalidades Atuais
- Autenticação de Usuário: Sistema de cadastro e login (atualmente validando contra o usuarios.csv).
- Cadastro de Vagas: Formulário para submissão de novas vagas de emprego.
- Cadastro de Currículos: Formulário para submissão de currículos, incluindo uma máscara de input (+XX XX 9XXXX-XXXX) para o campo de telefone.
- Visualização de Dados: Uma página protegida que exibe tabelas com todas as vagas e currículos cadastrados.
- Navegação Multi-Página: Estrutura de aplicação Streamlit com uma página principal de login (app.py) e páginas de funcionalidades (pages/).

## 🚀 Como Executar Localmente
Para testar a aplicação em sua máquina local, siga os passos abaixo.

**Pré-requisitos:** Python 3.8+, Git.

**Passos:**
1. Clone o repositório e navegue até a pasta do projeto:
    ```
    git clone https://github.com/Julia-Amadio/LabBD_App.git
    cd LabBD_App 
    ```
2. Crie um ambiente virtual:
    ```
    python -m venv .venv
    ```
3. Ative o ambiente virtual:
    - No **Windows**:
        - CMD (Prompt de Comando):
        ```
        .\.venv\Scripts\activate
        ```
        - No PowerShell:
        ```
        .\.venv\Scripts\Activate.ps1
        ```
    - No **macOS/Linux**:
    ```
    source .venv/bin/activate
    ```
4. Instale as dependências:
    ```
    pip install -r requirements.txt
    ```
5. Execute a aplicação Streamlit. O Streamlit irá executar o arquivo app.py (sua página de login) como ponto de entrada.
    ```
    streamlit run app.py
    ```
6. Acesse o app abrindo o endereço http://localhost:8501 no seu navegador.

## 👩‍💻 Autores
- Julia Amadio
- João Bastasini