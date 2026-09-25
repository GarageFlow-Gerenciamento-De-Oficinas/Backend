# GarageFlow — Backend

Backend for **GarageFlow**, a workshop management system designed for **Oficina Mecânica Avenida**.

The project aims to centralize and organize the operational processes of an automotive repair shop, replacing fragmented workflows based on paper records, messaging applications, and spreadsheets.

GarageFlow is being developed as a portfolio project with a strong focus on business rules, data integrity, automated testing, CI/CD, and maintainable software architecture.

---

## 📌 About the Project

The backend provides the REST API and implements the business rules required by the GarageFlow platform.

The planned system includes:

* User management
* Groups and permissions
* Authentication and authorization
* Customer management
* Vehicle management
* Service catalog
* Parts catalog
* Inventory management
* Service orders
* Quotes
* Service execution
* Parts usage
* Payments and adjustments
* Operational history
* Interruption and cancellation workflows
* Vehicle delivery

The application is designed around the principle that important operational and commercial information should remain traceable throughout its lifecycle.

Instead of relying on physical deletion whenever possible, the system uses mechanisms such as status transitions, active/inactive states, historical records, and compensating operations.

---

# 🏗️ Architecture

GarageFlow follows a Django-based backend architecture with PostgreSQL as its primary database.

```text
┌──────────────────────┐
│       Frontend       │
│                      │
│       Vue.js         │
└──────────┬───────────┘
           │
           │ HTTP / JSON
           ▼
┌──────────────────────┐
│       Backend        │
│                      │
│   Django + DRF       │
│                      │
│  ┌────────────────┐  │
│  │ Business Rules │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
           │ Django ORM
           ▼
┌──────────────────────┐
│     PostgreSQL       │
└──────────────────────┘
```

The development environment runs through Docker and can also be used through the VS Code Dev Container.

The backend separates responsibilities between API, validation, business logic, and persistence.

The general request flow is:

```text
HTTP Request
     │
     ▼
   View
     │
     ▼
 Serializer
     │
     ▼
  Service
     │
     ▼
   Model
     │
     ▼
PostgreSQL
```

Services are introduced when business logic becomes complex enough to benefit from being isolated from views and serializers.

The project intentionally avoids unnecessary abstractions and favors explicit business rules.

---

# 🛠️ Technology Stack

## Backend

* Python
* Django
* Django REST Framework
* PostgreSQL
* Django REST Framework Simple JWT
* drf-spectacular

## Infrastructure

* Docker
* Docker Compose
* Dev Containers

## Development

* Git
* GitLab
* GitHub
* VS Code
* pytest
* pytest-django

## Quality

* Automated tests
* CI/CD
* OpenAPI
* Swagger UI

---

# 📁 Project Structure

```text
garageflow/
│
├── .devcontainer/
│   └── devcontainer.json
│
├── .github/
│   └── workflows/
│       └── tests.yml
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
│   │   │   ├── activation.py
│   │   │   ├── email.py
│   │   │   └── invitation.py
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
├── pytest.ini
├── README.md
└── requirements.txt
```

The `.env` file is used locally and must not be committed to the repository.

---

# 🔐 Authentication

GarageFlow uses JWT-based authentication through **Django REST Framework Simple JWT**.

Users authenticate using their email address and password.

## Login

```text
POST /api/auth/login/
```

Example request:

```json
{
    "email": "user@example.com",
    "password": "password"
}
```

The API returns an access token and a refresh token.

The access token must be sent with authenticated requests using:

```text
Authorization: Bearer <access_token>
```

---

# 👤 User Management

GarageFlow uses a custom Django user model based on `AbstractUser`.

The `username` field is not used. Email is the unique authentication identifier.

Users currently contain information such as:

* Email
* Address
* Phone
* First name
* Last name
* Creation timestamp
* Update timestamp
* Activation timestamp
* Active/inactive status

The system distinguishes between **activation** and **active status**.

### Activated user

An activated user has:

* A defined password
* An `activated_at` timestamp

### Deactivated user

The `is_active` field is used to prevent a user from authenticating after administrative deactivation.

Deactivation does not physically remove the user from the database.

---

# ✉️ User Invitation and Activation

New users are created without a usable password and receive an invitation to activate their accounts.

The administrator never needs to define or know the user's password.

The current flow is:

```text
Administrator
      │
      ▼
Create User
      │
      ▼
User created without usable password
      │
      ▼
Create Invitation
      │
      ▼
Generate secure token
      │
      ▼
Send invitation email
      │
      ▼
User activates account
      │
      ▼
User defines password
      │
      ▼
Account activated
      │
      ▼
JWT Login
```

## Activation Endpoint

```text
POST /api/auth/activate/
```

Example request:

```json
{
    "token": "invitation-token",
    "password": "MyPassword123!"
}
```

Successful response:

```json
{
    "detail": "User activated successfully."
}
```

The activation endpoint does not require JWT authentication because the user has not authenticated yet.

---

# 🔑 Invitation Token Security

Invitation tokens are generated using a cryptographically secure source of randomness.

The original token is never stored directly in the database.

The process is:

```text
Original Token
      │
      ▼
   SHA-256
      │
      ▼
Token Hash
      │
      ▼
Database
```

When the user activates the account, the received token is hashed again and compared against the stored hash.

Each invitation has:

* A cryptographically secure random token
* A SHA-256 token hash
* A 24-hour expiration period
* A single-use restriction
* A usage timestamp
* An invalidation timestamp
* A creation timestamp

The `UserInvitation` model contains:

```text
user
token_hash
expires_at
used_at
invalidated_at
created_at
```

Invitation tokens are therefore treated as credentials and are not persisted in their original form.

---

# 🔄 Invitation Resend

Users who have not yet activated their accounts can receive a new invitation.

```text
POST /api/auth/resend-invitation/
```

Example request:

```json
{
    "email": "user@example.com"
}
```

The resend process is:

```text
Existing Invitation
        │
        ▼
Invalidate Previous Invitation
        │
        ▼
Create New Invitation
        │
        ▼
Generate New Token
        │
        ▼
Send Email
```

Previous invitations are not deleted.

Instead, they are marked with `invalidated_at`, preserving the invitation history.

The public API uses a generic response regardless of whether the email belongs to an eligible user.

This prevents the endpoint from exposing whether a specific email address is registered or already activated.

---

# ⚙️ Invitation Services

Invitation-related business logic is isolated in:

```text
backend/user/services/invitation.py
```

The service is responsible for:

* Generating invitation tokens
* Hashing tokens
* Creating invitations
* Defining expiration
* Invalidating previous invitations
* Resending invitations

Email delivery is handled separately by:

```text
backend/user/services/email.py
```

This keeps token management and email delivery as separate responsibilities.

---

# 🔓 Activation Service

Account activation logic is isolated in:

```text
backend/user/services/activation.py
```

The service is responsible for:

1. Receiving the invitation token.
2. Hashing the received token.
3. Locating the invitation.
4. Validating the invitation.
5. Checking whether it has already been used.
6. Checking whether it has been invalidated.
7. Checking whether it has expired.
8. Setting the user's password.
9. Setting `activated_at`.
10. Marking the invitation as used.

The activation operation is atomic.

If an error occurs during the operation, database changes performed within the transaction are rolled back.

---

# 🔒 Activation Rules

An invitation can only be used when:

* The token exists.
* The invitation has not been used.
* The invitation has not been invalidated.
* The invitation has not expired.

These conditions are handled separately so the system can distinguish between different invalid invitation states internally.

Passwords are never stored as plain text. Django's password hashing mechanism is responsible for securely storing user passwords.

---

# 👥 Groups and Permissions

GarageFlow is planned to use a role and permission system based on groups and granular permissions.

Users will be able to belong to multiple groups, and their effective permissions will be determined by the permissions granted through those groups.

The initial business roles are planned as:

* Administrator
* Attendant
* Mechanic

Permissions are modeled around resources and actions.

Examples:

```text
Resource: Customer
Action: View

Resource: Customer
Action: Create

Resource: Service Order
Action: Update

Resource: Inventory
Action: Move
```

The permission model is designed to allow new permissions to be introduced without relying exclusively on hard-coded roles.

The full authorization system is planned for a later development stage.

---

# 👤 Customers

Customer management is currently implemented as part of the backend.

Customers use `is_active` to represent their active status.

Important customer records are not physically deleted.

When a customer is no longer active, the record is deactivated while historical information remains available.

The customer API supports active/inactive filtering.

The system also enforces customer contact requirements according to the implemented validation rules.

Vehicles are associated with customers and remain part of the customer domain rather than being treated as an independent application.

---

# 🚗 Service Orders

Service Orders are one of the central business entities of GarageFlow.

The planned operational lifecycle is:

```text
Awaiting Evaluation
        ↓
Quote Awaiting Approval
        ↓
Quote Approved
        ↓
Service In Progress
        ↓
Testing
        ↓
Service Completed
        ↓
Payment Completed
        ↓
Vehicle Delivered
```

The workflow also supports business scenarios such as:

* Cancellation
* Interruption
* Regularization
* Complementary service orders
* Rework after failed testing

Service Order transitions are governed by business rules and are intended to be recorded in the service order history.

---

# 📦 Inventory

The inventory domain is designed around historical stock movements.

The system distinguishes between:

* Physical stock
* Reserved stock
* Available stock
* Safety stock

Available stock is calculated as:

```text
Available Stock = Physical Stock - Reserved Stock
```

Stock movements are treated as historical records.

Corrections should be represented through new compensating movements rather than deleting historical movements.

Parts reserved for Service Orders are also tracked separately from physical stock.

---

# 💰 Quotes and Historical Values

Commercial values must remain historically consistent.

When an operation records a service or part price, the value used by that operation should not change simply because the catalog is updated later.

For example:

```text
Current Part Price: R$ 150.00

Service Order Created:
Recorded Price: R$ 120.00

Catalog Price Updated:
R$ 150.00
```

The existing Service Order continues to use:

```text
R$ 120.00
```

This principle applies to relevant service, part, quote, payment, and operational values.

---

# 🧾 History and Auditability

GarageFlow is designed to preserve an operational history of important business events.

Service Order history is planned to record events such as:

* Status changes
* Data changes
* Quote changes
* Comments
* Customer communication
* Service execution
* Testing results
* Adjustments
* Cancellations
* Interruptions
* Other relevant operational events

Historical records are intended to remain immutable after creation.

---

# 🔒 Data Integrity

The system prioritizes the preservation of operational and commercial information.

Important entities should not be physically deleted when doing so could compromise historical information.

Depending on the domain, the system uses mechanisms such as:

* Active/inactive states
* Status transitions
* Cancellation states
* Compensating movements
* Historical records
* Timestamps

The objective is to maintain traceability throughout the lifecycle of the data.

---

# 📖 API Documentation

The API uses **OpenAPI** through `drf-spectacular`.

Swagger UI is available at:

```text
http://localhost:8000/api/docs/
```

The OpenAPI schema is available at:

```text
http://localhost:8000/api/schema/
```

API documentation is generated from the backend configuration and endpoint definitions.

Specific endpoints can use `drf-spectacular` annotations to provide additional request, response, and business context.

---

# 🧪 Testing

Automated tests are an integral part of the project.

The backend uses:

* pytest
* pytest-django
* Django REST Framework testing utilities

Tests cover both API behavior and business services.

Current test coverage includes customer management and the complete user invitation and activation flow.

## User and Invitation Tests

The invitation flow includes tests for:

* User creation
* Invitation creation
* Token generation
* Token hashing
* SHA-256 hash validation
* Invitation expiration
* Invitation invalidation
* Single-use invitation enforcement
* Invitation resend
* Email delivery

## Account Activation Tests

The activation flow includes tests for:

* Valid activation
* Invalid tokens
* Expired invitations
* Used invitations
* Invalidated invitations
* Password validation
* Password definition
* User activation
* `activated_at`
* `used_at`
* Authentication after activation

## API Tests

API tests cover:

* User creation
* User retrieval
* User updates
* User deactivation
* Active/inactive filtering
* Invitation activation
* Invitation resend
* Invalid email input
* Unknown email addresses
* Already activated users

Run the complete test suite with:

```bash
pytest
```

---

# 🔄 CI/CD

GarageFlow uses automated CI/CD pipelines to validate changes.

The project currently includes CI configurations for GitLab and GitHub.

The test suite acts as a quality gate for merge requests.

```text
Feature Branch
      │
      ▼
    Commit
      │
      ▼
     Push
      │
      ▼
Merge Request
      │
      ▼
Automated CI
      │
      ▼
Install Dependencies
      │
      ▼
Database Setup
      │
      ▼
Run Tests
      │
   ┌──┴──┐
   ▼     ▼
 PASS   FAIL
   │     │
   ▼     ▼
Merge  Blocked
Allowed
```

A merge request must pass the automated test suite before being merged.

This quality gate is intended to prevent regressions from reaching the main development branch.

---

# 🐳 Development Environment

GarageFlow uses Docker to provide a consistent development environment.

## Requirements

* Docker
* Docker Compose
* VS Code
* Dev Containers extension

## Configuration

Clone the repository:

```bash
git clone <repository-url>

cd garageflow
```

Create the local environment file:

```bash
cp .env.example .env
```

Configure the required environment variables.

Example:

```env
POSTGRES_DB=garageflow
POSTGRES_USER=garageflow
POSTGRES_PASSWORD=your_password

DB_NAME=garageflow
DB_USER=garageflow
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your-secret-key
DEBUG=True
```

---

# 🚀 Running with Docker

Build and start the development environment:

```bash
docker compose up --build
```

The backend will be available at:

```text
http://localhost:8000
```

Run migrations with:

```bash
docker compose exec web python manage.py migrate
```

Run the test suite with:

```bash
docker compose exec web pytest
```

Swagger UI:

```text
http://localhost:8000/api/docs/
```

---

# 🧑‍💻 Dev Container

The project includes a VS Code Dev Container configuration.

After opening the project in VS Code, use:

```text
Ctrl + Shift + P
```

Then select:

```text
Dev Containers: Reopen in Container
```

The workspace is available inside the container at:

```text
/workspace
```

The Django project is located at:

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
* [x] Environment variables
* [x] Dev Container
* [x] Git
* [x] Initial application structure
* [x] OpenAPI / Swagger
* [x] JWT authentication
* [x] CI/CD quality gate

## Users and Authorization

* [x] Custom user model
* [x] Email-based authentication
* [x] User management API
* [x] User activation flow
* [x] Invitation system
* [x] Invitation token hashing
* [x] Invitation expiration
* [x] Single-use invitations
* [x] Invitation invalidation
* [x] Invitation resend
* [x] Invitation email service
* [x] Activation API
* [x] Tests for invitation and activation flows
* [ ] User groups
* [ ] Permissions
* [ ] Resource/action permission model
* [ ] Endpoint-level authorization

## Customers and Vehicles

* [x] Customer management
* [x] Customer deactivation
* [x] Vehicle management
* [ ] Customer document support

## Catalogs

* [ ] Service catalog
* [ ] Parts catalog

## Inventory

* [ ] Physical stock
* [ ] Reserved stock
* [ ] Available stock calculation
* [ ] Stock movements
* [ ] Safety stock
* [ ] Inventory alerts

## Service Orders

* [ ] Service Order creation
* [ ] Service Order lifecycle
* [ ] Quotes
* [ ] Service Order items
* [ ] Parts usage
* [ ] Service execution
* [ ] Testing
* [ ] Interruption
* [ ] Cancellation
* [ ] Regularization
* [ ] Complementary Service Orders
* [ ] Vehicle delivery

## Finance

* [ ] Payments
* [ ] Multiple payment methods
* [ ] Adjustments
* [ ] Balance management

## History

* [ ] Service Order history
* [ ] Audit trail
* [ ] Inventory history
* [ ] Financial history

## Quality and Delivery

* [x] Automated tests
* [x] OpenAPI documentation
* [x] Swagger UI
* [x] CI pipeline
* [x] Merge request quality gate
* [ ] Linting
* [ ] Test coverage reporting
* [ ] Automated build
* [ ] Automated deployment

## Frontend

* [ ] Vue.js application
* [ ] Authentication interface
* [ ] User management interface
* [ ] Customer management
* [ ] Vehicle management
* [ ] Service Order workflow
* [ ] Inventory management
* [ ] Financial management

---

# 📚 Documentation

The project documentation is maintained alongside the source code in this repository.

As the system grows, additional documentation will be introduced for:

* Architecture
* Domain rules
* API behavior
* Architectural decisions
* Development practices

The README currently serves as the primary project documentation.

---

# 👨‍💻 Development

GarageFlow is being developed by **Jean França** as a portfolio and software engineering project.

The project is intended to demonstrate not only knowledge of specific technologies, but also the ability to:

* Model complex business rules
* Design maintainable systems
* Develop REST APIs
* Implement authentication and authorization
* Preserve historical data integrity
* Build automated tests
* Document APIs
* Implement CI/CD practices
* Develop a complete software product incrementally
