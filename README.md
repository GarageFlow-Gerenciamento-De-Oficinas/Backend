# GarageFlow — Backend

Backend do **GarageFlow**, sistema de gerenciamento desenvolvido para a **Oficina Mecânica Avenida**.

O projeto tem como objetivo centralizar e organizar os processos operacionais de uma oficina mecânica, substituindo controles manuais realizados por papel, WhatsApp e planilhas.

---

## 📌 Sobre o projeto

O backend é responsável por fornecer a API e implementar as principais regras de negócio do sistema, incluindo:

* Gerenciamento de usuários, grupos e permissões
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

---

## 🛠️ Tecnologias

### Backend

* Python
* Django
* Django REST Framework
* PostgreSQL

### Infraestrutura

* Docker
* Docker Compose
* Dev Containers

### Desenvolvimento

* Git
* GitHub
* VS Code

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
│   └── manage.py
│
├── docker/
│   └── Dockerfile
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── requirements.txt
```

> O arquivo `.env` é utilizado localmente e não deve ser versionado.

---

## 🔐 Usuários, grupos e permissões

O sistema utiliza um modelo de autorização baseado em **grupos e permissões**.

Os usuários podem pertencer a múltiplos grupos e suas permissões são determinadas pela união das permissões concedidas aos grupos dos quais participam.

Os perfis inicialmente previstos são:

* **Administrador**
* **Atendente**
* **Mecânico**

A autorização será aplicada de acordo com o recurso e a ação que o usuário está tentando executar.

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

---

## 🚗 Ordens de serviço

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

## 📦 Controle de estoque

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

## 💰 Orçamentos e valores históricos

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

## 🧾 Histórico

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

## 🔒 Integridade dos dados

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

## 🐳 Ambiente de desenvolvimento

O projeto utiliza Docker para padronizar o ambiente de desenvolvimento.

### Pré-requisitos

* Docker
* Docker Compose
* VS Code
* Extensão Dev Containers

### Configuração

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

## 🚀 Executando com Docker

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

---

## 🧑‍💻 Dev Container

O projeto possui configuração para desenvolvimento através do VS Code Dev Containers.

Após abrir o projeto no VS Code:

```text
Ctrl + Shift + P
```

selecione:

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

## 🧪 Testes

O projeto utiliza o sistema de testes do Django.

Para executar todos os testes:

```bash
python manage.py test
```

Ou, utilizando Docker:

```bash
docker compose exec web python manage.py test
```

Os testes serão ampliados conforme novas regras de negócio forem implementadas.

---

## 🗺️ Roadmap

### Foundation

* [x] Docker
* [x] PostgreSQL
* [x] Django
* [x] Variáveis de ambiente
* [x] Dev Container
* [x] Git
* [ ] Estrutura inicial das aplicações

### Usuários e autorização

* [ ] Usuário
* [ ] Grupos
* [ ] Permissões
* [ ] Autorização por recurso/ação

### Cadastros

* [ ] Clientes
* [ ] Veículos
* [ ] Serviços
* [ ] Peças

### Estoque

* [ ] Estoque físico
* [ ] Estoque reservado
* [ ] Movimentações
* [ ] Alertas de estoque

### Ordens de serviço

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

### Financeiro

* [ ] Pagamentos
* [ ] Múltiplas formas de pagamento
* [ ] Abatimentos
* [ ] Controle de saldo

### Histórico

* [ ] Histórico da OS
* [ ] Auditoria de alterações
* [ ] Histórico de estoque
* [ ] Histórico financeiro

---

## 📚 Documentação

A documentação geral do produto e suas decisões arquiteturais serão mantidas no repositório da organização.

**GarageFlow**

Sistema de gerenciamento para oficinas mecânicas.

---

## 👨‍💻 Desenvolvimento

Projeto desenvolvido por **Jean França** como projeto de portfólio e estudo de engenharia de software.

O objetivo é demonstrar não apenas conhecimento de tecnologias, mas também capacidade de modelar regras de negócio, projetar sistemas, preservar integridade de dados e construir uma aplicação completa.
