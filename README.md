# GarageFlow — Backend

Backend do **GarageFlow**, sistema de gerenciamento desenvolvido para a **Oficina Mecânica Avenida**.

O projeto tem como objetivo centralizar e organizar os processos operacionais de uma oficina mecânica, substituindo controles manuais realizados por papel, WhatsApp e planilhas.

---

## 📌 Sobre o projeto

O backend é responsável por fornecer a API e implementar as principais regras de negócio do sistema, incluindo:

* Gerenciamento de usuários, grupos e permissões
* Autenticação e autorização
* Cadastro de clientes
* Cadastro e gerenciamento de veículos
* Catálogo de serviços
* Catálogo de peças
* Controle de estoque
* Ordens de serviço
* Orçamentos
* Execução de serviços
* Controle de peças utilizadas
* Pagamentos e abatimentos
* Histórico de alterações e eventos
* Fluxos de interrupção e cancelamento
* Controle de entrega dos veículos

A aplicação foi projetada considerando a necessidade de preservar informações históricas e manter rastreabilidade das operações realizadas pelos usuários.

---

## 🏗️ Arquitetura

O backend utiliza uma arquitetura baseada em Django, com PostgreSQL como banco de dados principal.

```text
┌──────────────────────┐
│       Frontend       │
│         Vue.js       │
└──────────┬───────────┘
           │
           │ HTTP / API
           ▼
┌──────────────────────┐
│       Backend        │
│       Django         │
│                      │
│  ┌────────────────┐  │
│  │ Regras negócio │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     PostgreSQL       │
└──────────────────────┘
```

O ambiente de desenvolvimento é executado através de Docker e pode ser utilizado através do Dev Container do VS Code.

A aplicação separa responsabilidades entre diferentes camadas, mantendo regras de negócio mais complexas em **services**, enquanto serializers são responsáveis pela validação e transformação dos dados e views pela exposição dos endpoints HTTP.

---

## 🛠️ Tecnologias

### Backend

* Python
* Django
* Django REST Framework
* PostgreSQL
* Simple JWT
* drf-spectacular

### Infraestrutura

* Docker
* Docker Compose
* Dev Containers

### Desenvolvimento

* Git
* GitLab
* VS Code

### Qualidade

* Testes automatizados
* CI/CD
* OpenAPI / Swagger

---

## 📁 Estrutura do projeto

```text
Backend/

├── .devcontainer/
│   └── devcontainer.json
│
├── backend/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── client/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests.py
│   │
│   ├── user/
│   │   ├── models.py
│   │   ├── serializers/
│   │   ├── services/
│   │   │   ├── invitation.py
│   │   │   └── activation.py
│   │   ├── views/
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── manage.py
│
├── docker/
│   └── Dockerfile
│
├── .env.example
├── .gitignore
├── .gitlab-ci.yml
├── docker-compose.yml
├── README.md
└── requirements.txt
```

> O arquivo `.env` é utilizado localmente e não deve ser versionado.

---

# 🔐 Autenticação e autorização

O sistema utiliza autenticação baseada em **JWT (JSON Web Token)**.

A autenticação utiliza o **Django REST Framework Simple JWT**.

O usuário utiliza seu e-mail e senha para obter os tokens de autenticação através da API.

## Login

```text
POST /api/auth/login/
```

Exemplo de requisição:

```json
{
    "email": "usuario@email.com",
    "password": "senha"
}
```

A API retorna um `access token` e um `refresh token`.

O `access token` deve ser enviado nas requisições autenticadas através do header:

```text
Authorization: Bearer <access_token>
```

---

# 👥 Usuários, grupos e permissões

O sistema utiliza um modelo de autorização baseado em **grupos e permissões**.

Os usuários podem pertencer a múltiplos grupos e suas permissões são determinadas pela união das permissões concedidas aos grupos dos quais participam.

Os perfis inicialmente previstos são:

* **Administrador**
* **Atendente**
* **Mecânico**

As permissões são estruturadas considerando o recurso e a ação que o usuário está tentando executar.

Exemplos:

```text
Recurso: Cliente
Ação: visualizar

Recurso: Cliente
Ação: criar

Recurso: Ordem de Serviço
Ação: atualizar

Recurso: Estoque
Ação: movimentar
```

Esse modelo permite que novas permissões sejam adicionadas sem depender exclusivamente de papéis fixos no código.

A implementação da autorização específica por endpoint será realizada posteriormente através do sistema de permissões.

---

# 👤 Usuários

O GarageFlow utiliza um **User Model customizado**, baseado no `AbstractUser` do Django.

O sistema utiliza o **e-mail como identificador de autenticação**, não utilizando o campo `username`.

Os usuários possuem informações como:

* E-mail
* Endereço
* Telefone
* Data de criação
* Data de atualização
* Data de ativação
* Status de atividade

O modelo também diferencia dois conceitos importantes:

### Usuário ativado

O usuário possui uma senha definida e uma data registrada em `activated_at`.

### Usuário desativado

O campo `is_active` é utilizado para impedir o acesso de um usuário que foi administrativamente desativado.

A criação de usuários foi projetada para não permitir que administradores definam ou conheçam a senha do usuário.

---

## ✉️ Convites de ativação

O cadastro de um usuário utiliza um fluxo baseado em **convite de ativação**.

O fluxo previsto é:

```text
Administrador
      │
      ▼
Cria usuário
      │
      ▼
Usuário criado sem senha utilizável
      │
      ▼
Geração de convite
      │
      ▼
Token de ativação
      │
      ▼
Usuário recebe convite
      │
      ▼
POST /api/auth/activate/
      │
      ▼
Define própria senha
      │
      ▼
Conta ativada
      │
      ▼
POST /api/auth/login/
```

O administrador não precisa conhecer a senha do usuário em nenhum momento.

---

## 🔑 Segurança dos tokens de convite

Os tokens de ativação são gerados utilizando uma fonte criptograficamente segura de aleatoriedade.

O token original **não é armazenado diretamente no banco de dados**.

O fluxo utilizado é:

```text
Token original
      │
      ▼
SHA-256
      │
      ▼
Hash armazenado no banco
```

Quando o usuário tenta ativar a conta, o token recebido é novamente transformado em hash e comparado com o valor armazenado.

Isso reduz o impacto de uma eventual exposição dos dados persistidos.

Os convites possuem:

* Token aleatório de alta entropia
* Hash SHA-256 armazenado no banco
* Prazo de validade de 24 horas
* Uso único
* Registro da data de utilização

O modelo `UserInvitation` mantém:

```text
user
token_hash
expires_at
used_at
created_at
```

O token também não pode ser reutilizado depois da ativação.

---

## ⚙️ Service de convites

A lógica de geração de convites foi isolada em um service específico:

```text
user/services/invitation.py
```

Esse service é responsável por:

* Gerar o token
* Gerar o hash do token
* Definir o prazo de expiração
* Criar o registro `UserInvitation`

A separação dessa lógica evita que regras de segurança e geração de tokens fiquem diretamente nas views ou serializers.

---

## 🔓 Ativação de usuário

A ativação também possui um service próprio:

```text
user/services/activation.py
```

O service é responsável por:

1. Receber o token;
2. Gerar o hash correspondente;
3. Localizar o convite;
4. Validar sua existência;
5. Verificar se já foi utilizado;
6. Verificar se está expirado;
7. Definir a senha do usuário;
8. Registrar `activated_at`;
9. Registrar `used_at`.

A operação utiliza uma transação atômica para garantir que a ativação seja realizada de forma consistente.

Caso alguma etapa da operação falhe, as alterações realizadas dentro da transação são revertidas.

---

## 🔐 Regras de ativação

Um convite somente pode ser utilizado quando:

* O token é válido;
* O convite ainda não foi utilizado;
* O convite ainda não expirou.

As situações são tratadas separadamente:

```text
Token inválido
→ Convite inválido

Token já utilizado
→ Este convite já foi utilizado.

Token expirado
→ Este convite expirou.
```

O usuário define sua própria senha durante a ativação.

A senha não é armazenada em texto puro. O Django realiza o armazenamento através do mecanismo de hashing de senhas do próprio framework.

---

## 🌐 Endpoint de ativação

A ativação é disponibilizada através de:

```text
POST /api/auth/activate/
```

O endpoint não exige autenticação JWT, pois o usuário ainda não possui uma sessão autenticada durante o processo de ativação.

### Requisição

```json
{
    "token": "token-do-convite",
    "password": "MinhaSenha123!"
}
```

### Resposta

```json
{
    "detail": "Usuário ativado com sucesso."
}
```

O endpoint está documentado através do OpenAPI e disponível no Swagger.

---

# 👤 Clientes

O cadastro de clientes possui uma regra de negócio que exige que o cliente possua pelo menos um meio de contato:

* E-mail
* Telefone

Um cliente não pode ser fisicamente excluído do banco de dados.

Quando um cliente deixa de ser utilizado, seu registro é **desativado**, preservando os dados históricos.

O modelo utiliza o campo:

```text
is_active
```

A API utiliza o seguinte comportamento:

```text
GET /api/clients/
```

Retorna somente clientes ativos.

Para consultar clientes ativos:

```text
GET /api/clients/?is_active=true
```

Para consultar clientes inativos:

```text
GET /api/clients/?is_active=false
```

Uma requisição `DELETE` não remove fisicamente o registro. Ela apenas altera o cliente para inativo.

Essa abordagem preserva a integridade histórica dos dados.

---

# 📖 Documentação da API

A API utiliza **OpenAPI** para geração automática da documentação.

A interface **Swagger** está disponível em:

```text
/api/docs/
```

O schema OpenAPI pode ser acessado através de:

```text
/api/schema/
```

A documentação é gerada a partir dos endpoints e configurações da própria API, permitindo que a documentação acompanhe a evolução do backend.

Os endpoints que possuem comportamentos específicos podem utilizar recursos do `drf-spectacular` para complementar a documentação automática.

O endpoint de ativação de usuário, por exemplo, possui documentação explícita de seu request e response.

---

# 🚗 Ordens de serviço

A Ordem de Serviço é uma das principais entidades do sistema.

O fluxo operacional previsto inclui:

```text
Aguardando avaliação
        ↓
Orçamento aguardando aprovação
        ↓
Orçamento aprovado
        ↓
Serviço em execução
        ↓
Em testes
        ↓
Serviço finalizado
        ↓
Pagamento efetuado
        ↓
Veículo entregue
```

Além do fluxo normal, existem fluxos específicos para:

* Cancelamento
* Interrupção
* Regularização
* Ordens de serviço complementares
* Reexecução de serviços após falha em testes

As transições de estado são controladas pelas regras de negócio e registradas no histórico da ordem.

---

# 📦 Controle de estoque

O estoque diferencia:

* Estoque físico
* Estoque reservado
* Estoque disponível
* Estoque de segurança

O estoque disponível é calculado considerando as quantidades já reservadas para ordens de serviço.

```text
Disponível = Estoque físico - Estoque reservado
```

As movimentações de estoque são históricas e não devem ser simplesmente apagadas.

Correções são realizadas através de novas movimentações compensatórias, preservando a rastreabilidade.

O sistema também registra as reservas de peças associadas às ordens de serviço.

---

# 💰 Orçamentos e valores históricos

Valores comerciais importantes são preservados no momento em que uma operação é criada.

Isso inclui:

* Preço do serviço
* Preço da peça
* Custo da peça
* Quantidade aprovada
* Valores de orçamento
* Quantidades efetivamente utilizadas
* Pagamentos
* Abatimentos

Dessa forma, uma alteração futura no catálogo não modifica informações de operações antigas.

Por exemplo:

```text
Preço atual da peça: R$ 150,00

OS criada:
Preço registrado na OS: R$ 120,00

Preço posteriormente alterado:
R$ 150,00
```

A OS continua utilizando o valor histórico de R$ 120,00.

---

# 🧾 Histórico

Operações importantes possuem rastreabilidade através de históricos.

O histórico de uma Ordem de Serviço pode registrar:

* Alterações de status
* Alterações de dados
* Criação e alterações de orçamento
* Comentários
* Comunicação com cliente
* Responsabilidade por serviços
* Início da execução
* Falhas em testes
* Abatimentos
* Cancelamentos
* Interrupções
* Eventos relacionados à execução

Cada evento possui o usuário responsável e o momento em que ocorreu.

O histórico é considerado imutável.

---

# 🔒 Integridade dos dados

O sistema prioriza a preservação de informações operacionais e comerciais.

Entidades importantes não são fisicamente removidas quando isso poderia comprometer o histórico.

Em vez disso, são utilizados mecanismos como:

* Status
* Flags de ativo/inativo
* Cancelamentos
* Movimentações compensatórias
* Históricos

Isso permite manter a rastreabilidade das operações mesmo após alterações posteriores.

---

# 🧪 Testes

O projeto utiliza o sistema de testes do Django e Django REST Framework para validar as regras e comportamentos da API.

Atualmente existem testes automatizados para a API de clientes, cobrindo cenários como:

* Criação de cliente válido
* Validação de dados obrigatórios
* Validação de contato
* Tentativa de cadastro duplicado
* Listagem
* Consulta individual
* Atualização
* Atualização com dados inválidos
* Consulta de clientes ativos
* Consulta de clientes inativos
* Desativação de clientes
* Garantia de que registros desativados permanecem no banco

Também existem testes relacionados ao fluxo de convite e ativação de usuários.

### Convites

Os testes cobrem:

* Criação de convite
* Geração de token
* Armazenamento somente do hash
* Validação do hash SHA-256
* Prazo de expiração

### Ativação

Os testes cobrem:

* Ativação com token válido
* Token inválido
* Convite expirado
* Convite já utilizado
* Garantia de uso único do convite
* Definição da senha
* Ativação do usuário
* Registro de `activated_at`
* Registro de `used_at`

### Serializer de ativação

Também existem testes para:

* Token obrigatório
* Senha obrigatória
* Tamanho mínimo da senha
* Dados válidos
* Token inválido

Para executar todos os testes:

```bash
python manage.py test
```

Ou utilizando Docker:

```bash
docker compose exec web python manage.py test
```

A suíte de testes será ampliada conforme novas regras de negócio forem implementadas.

---

# 🔄 Integração contínua

O projeto utiliza **GitLab CI/CD** para automatizar a execução dos testes.

O pipeline é definido através do arquivo:

```text
.gitlab-ci.yml
```

A rotina de CI prepara um ambiente isolado contendo Python e PostgreSQL, instala as dependências do projeto, executa as migrations e executa a suíte completa de testes.

Fluxo previsto:

```text
Feature Branch
      ↓
   Commit
      ↓
    Push
      ↓
Merge Request
      ↓
 GitLab CI/CD
      ↓
 Instala dependências
      ↓
 PostgreSQL
      ↓
    Migrations
      ↓
 Testes automatizados
      ↓
 ┌────┴────┐
 ↓         ↓
PASS      FAIL
 ↓         ↓
Merge    Bloqueio
```

O pipeline funciona como **quality gate**, impedindo que alterações sejam incorporadas à branch principal enquanto a rotina automatizada de testes estiver falhando.

---

# 🐳 Ambiente de desenvolvimento

O projeto utiliza Docker para padronizar o ambiente de desenvolvimento.

## Pré-requisitos

* Docker
* Docker Compose
* VS Code
* Extensão Dev Containers

## Configuração

Clone o repositório:

```bash
git clone <repository-url>

cd Backend
```

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Configure as variáveis necessárias.

Exemplo:

```env
POSTGRES_DB=garageflow
POSTGRES_USER=garageflow
POSTGRES_PASSWORD=sua_senha

DB_NAME=garageflow
DB_USER=garageflow
DB_PASSWORD=sua_senha
DB_HOST=db
DB_PORT=5432

SECRET_KEY=sua-secret-key
DEBUG=True
```

---

# 🚀 Executando com Docker

Construa e inicialize os containers:

```bash
docker compose up --build
```

O backend estará disponível em:

```text
http://localhost:8000
```

Para executar as migrations:

```bash
docker compose exec web python manage.py migrate
```

Para executar os testes:

```bash
docker compose exec web python manage.py test
```

A documentação Swagger estará disponível em:

```text
http://localhost:8000/api/docs/
```

---

# 🧑‍💻 Dev Container

O projeto possui configuração para desenvolvimento através do VS Code Dev Containers.

Após abrir o projeto no VS Code:

```text
Ctrl + Shift + P
```

Selecione:

```text
Dev Containers: Reopen in Container
```

O workspace será aberto dentro do container em:

```text
/workspace
```

A estrutura interna será equivalente à raiz do projeto:

```text
/workspace

├── .devcontainer/
├── backend/
├── docker/
├── .env
├── docker-compose.yml
└── ...
```

O Django permanece localizado em:

```text
/workspace/backend
```

---

# 🗺️ Roadmap

## Foundation

* [x] Docker
* [x] PostgreSQL
* [x] Django
* [x] Django REST Framework
* [x] Variáveis de ambiente
* [x] Dev Container
* [x] Git
* [x] Estrutura inicial das aplicações
* [x] Swagger / OpenAPI
* [x] Autenticação JWT
* [x] CI/CD completo

## Usuários e autorização

* [x] Usuário customizado
* [x] Autenticação por e-mail
* [x] Grupos
* [x] Permissões
* [x] Estrutura de permissões por recurso/ação
* [x] Fluxo de convite de ativação
* [x] Token de convite com hash
* [x] Expiração de convite
* [x] Uso único de convite
* [x] Endpoint de ativação de usuário
* [x] Testes do fluxo de convite e ativação
* [ ] Endpoint de gerenciamento de usuários
* [ ] Reenvio de convite
* [ ] Autorização completa por endpoint

## Cadastros

* [x] Clientes
* [x] Veículos
* [ ] Serviços
* [ ] Peças

## Estoque

* [ ] Estoque físico
* [ ] Estoque reservado
* [ ] Movimentações
* [ ] Alertas de estoque

## Ordens de serviço

* [ ] Criação da OS
* [ ] Orçamentos
* [ ] Itens de serviço
* [ ] Peças utilizadas
* [ ] Execução
* [ ] Testes
* [ ] Interrupção
* [ ] Cancelamento
* [ ] Regularização
* [ ] Entrega do veículo

## Financeiro

* [ ] Pagamentos
* [ ] Múltiplas formas de pagamento
* [ ] Abatimentos
* [ ] Controle de saldo

## Histórico

* [ ] Histórico da OS
* [ ] Auditoria de alterações
* [ ] Histórico de estoque
* [ ] Histórico financeiro

## Qualidade e entrega

* [x] Testes automatizados
* [x] Documentação OpenAPI
* [x] Swagger UI
* [x] Pipeline inicial de CI
* [x] Pipeline obrigatório para Merge Requests
* [ ] Lint
* [ ] Relatório de cobertura de testes
* [ ] Build automatizado
* [ ] Deploy automatizado

---

# 📚 Documentação

A documentação geral do produto e suas decisões arquiteturais serão mantidas no repositório da organização.

**GarageFlow**

Sistema de gerenciamento para oficinas mecânicas.

---

# 👨‍💻 Desenvolvimento

Projeto desenvolvido por **Jean França** como projeto de portfólio e estudo de engenharia de software.

O objetivo é demonstrar não apenas conhecimento de tecnologias, mas também capacidade de:

* Modelar regras de negócio
* Projetar sistemas
* Desenvolver APIs
* Implementar autenticação e autorização
* Preservar integridade de dados
* Criar testes automatizados
* Documentar APIs
* Aplicar práticas de integração contínua
* Construir uma aplicação completa
