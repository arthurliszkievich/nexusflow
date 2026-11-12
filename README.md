# ⚡ NexusFlow — Plataforma Corporativa de Gestão de Demandas & RH (HCM)

O **NexusFlow** é uma plataforma corporativa para gestão de demandas, workflows internos de RH (férias, requisições de equipamentos, chamados departamentais) e triagem inteligente com IA, projetada com foco em alta performance, consistência transacional ACID e padrões arquiteturais modernos.

Projeto desenvolvido com o objetivo de aprofundar na prática padrões de arquitetura corporativa, cache distribuído com **Redis**, consumo e interfaces com **React**, e boas práticas no ecossistema **Python/Django**.

---

## 🛠️ Stack Tecnológica & Arquitetura

* **Backend:** Python 3.12+ | Django 5.1+ | Django REST Framework (DRF)
* **Banco Relacional:** PostgreSQL 16 (Modelagem relacional estrita, constraints de integridade e transações ACID)
* **Cache Distribuído:** Redis 7 via `django-redis` (Padrão Cache-Aside com TTL e invalidação cirúrgica)
* **Segurança & Config:** Twelve-Factor App via `django-environ` e autenticação JWT (`djangorestframework-simplejwt`)
* **Qualidade de Software:** TDD com Pytest (`pytest-django`, `model-bakery` e fixtures)
* **Infraestrutura:** Docker & Docker Compose com Healthchecks e Service Discovery
* **Frontend:** React + Vite (Interface moderna consumindo a API REST)

---

## 🚀 Como Executar o Projeto com Docker

### 1. Clonar e Configurar Variáveis de Ambiente
```bash
cp .env.example .env
```

### 2. Construir e Subir os Containers
```bash
docker compose up -d --build
```
Os seguintes serviços estarão disponíveis:
* **API Django:** `http://localhost:8000`
* **PostgreSQL 16:** `localhost:5434` (porta interna `db:5432`)
* **Redis 7:** `localhost:6379`

### 3. Rodar a Suíte de Testes (TDD)
```bash
docker compose exec web pytest
```
*(ou localmente via venv: `pytest`)*

---

## 🗺️ Roadmap de Desenvolvimento

- [x] **Fase 1:** Infraestrutura, Docker Compose, Twelve-Factor Config, Redis, Postgres e Pytest.
- [ ] **Fase 2:** Modelagem Relacional, Constraints estritas, ORM e Prevenção de N+1 Queries.
- [ ] **Fase 3:** Service Layer, TDD Pragmático, Concorrência (`select_for_update`) e Motor de IA.
- [ ] **Fase 4:** ViewSets DRF, Permissões granulares e Camada de Cache com Redis.
- [ ] **Fase 5:** Frontend React (Vite) integrado e testes de ponta a ponta.

---
Desenvolvido por **Arthur** como projeto prático de engenharia de software e domínio de stack.
