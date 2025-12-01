# 🔐 Documentação de perfis e permissões

Este documento detalha os níveis de acesso, funcionalidades e restrições de cada tipo de usuário no Sistema de Gestão de Vagas e Currículos.

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