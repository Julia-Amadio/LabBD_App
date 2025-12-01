# LabBD_App: Sistema de Gerenciamento de Vagas e Currículos

Este repositório contém o código-fonte de um aplicativo web para gerenciamento de vagas de emprego e currículos, desenvolvido como projeto para a disciplina de Laboratório de Banco de Dados. A aplicação é construída em Python usando a biblioteca Streamlit.

## 🌐 Deploy do projeto
O deploy foi feito por meio da Streamlit Community Cloud. Este projeto está hospedado na URL https://fakelinkedinlabbd.streamlit.app/.

## ✨ Funcionalidades atuais
- Cadastro de Vagas: Formulário para submissão de novas vagas de emprego.
- Cadastro de Currículos: Formulário para submissão de currículos, incluindo uma máscara de input (+XX XX 9XXXX-XXXX) para o campo de telefone.
- Visualização de Dados: Uma página protegida que exibe tabelas com todas as vagas e currículos cadastrados.
- Navegação Multi-Página: Estrutura de aplicação Streamlit com uma página principal de login (Login.py) e páginas de funcionalidades (pages/).

# 🔐 Documentação de perfis e permissões

O sistema utiliza controle de acesso baseado em papéis (RBAC - Role-Based Access Control), definido pelo campo tipo_usuario na coleção usuarios do MongoDB.

## 👥 Perfis de Usuário

**Existem três perfis distintos no sistema:**

### 1. 🎓 Candidato (```tipo_usuario: "candidato"```)

Usuário final que busca oportunidades de emprego.

- Objetivo: cadastrar seu perfil profissional e encontrar vagas compatíveis.
- Restrições:
  - Não pode visualizar currículos de outros candidatos;
  - Não pode cadastrar vagas.

**Lógica de dados:**
possui um campo ```id_curriculo``` no banco de dados.
- Estado inicial: ```id_curriculo: null``` (permite acessar o formulário de cadastro).
- Estado pós-cadastro (exemplo): ```id_curriculo: 105``` (o formulário é bloqueado e substituído pela visualização **"Meu Currículo"**).

### 2. 🏢 Empregador (```tipo_usuario: "empregador"```)

Representante de uma empresa que busca talentos.
- Objetivo: divulgar vagas e encontrar candidatos qualificados.
- Restrições:
  - Não pode cadastrar um currículo pessoal;
  - Não pode criar vagas associadas a outras empresas.

**Lógica de Dados:**
possui o campo empresa fixo no cadastro (ex: "Microsoft Brasil").
Ao listar vagas, o sistema aplica um filtro automático para exibir apenas registros onde ```empresa == Usuário.empresa```.

### 3. 🔧 Administrador (```tipo_usuario: "admin"```)

Superusuário responsável pela gestão e manutenção do sistema.

- Objetivo: moderação, cadastro manual e manutenção técnica.
- Privilégios exclusivos:
  - Acesso a ferramentas de sistema (ex: Gerador de Embeddings/Backfill);
  - Visão global de todas as vagas e currículos sem filtros;
  - Pode cadastrar múltiplos currículos (para fins de inserção manual de dados).

# 🚀 Como executar localmente
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
    streamlit run Login.py
    ```
6. Acesse o app abrindo o endereço http://localhost:8501 no seu navegador.

# 👩‍💻 Autores
- Julia Amadio
- João Bastasini