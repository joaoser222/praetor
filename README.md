# PraetorAPI: Full-Stack FastAPI Modular Boilerplate

A professional, production-ready full-stack boilerplate. It combines a **FastAPI** backend (inspired by Django's modularity) with a modern **React + Vite** frontend, all orchestrated by a powerful automated CLI.

---

### 📚 [Explore the Detailed Documentation](./docs/getting_started.md)
*Architecture, Authentication, CLI, Background Tasks, and more.*

---

## 🔥 Key Features

### 💻 Backend (FastAPI)
- **Modular App Structure**: Independent "apps" for clean domain separation (à la Django).
- **Layered Architecture**: Repository Pattern & Service Layer for robust business logic.
- **Advanced Auth & RBAC**: Ready-to-use JWT (Access/Refresh) and Role-Based Access Control.
- **Automated CLI**: `manage.py` for generating code, migrations, users, and permissions.
- **Async & Task-Ready**: Native `async/await` support and Celery + Redis integration.

### 🎨 Frontend (React + Vite)
- **Domain-Driven Design**: Organized by features (`src/features/{app}/{entity}`).
- **Zero-Config Routing**: Automatic discovery of routes from feature directories.
- **Modern UI Stack**: Tailwind CSS, **shadcn/ui** components, and Lucide icons.
- **DataTable by Default**: Powerful data handling with **TanStack Table**.
- **Validated Forms**: Schema-based validation using **React Hook Form** + **Zod**.

## 🛠 Why PraetorAPI?

PraetorAPI is built to accelerate development without sacrificing architectural integrity. It bridges the gap between the speed of FastAPI and the organized patterns required for large-scale applications.

1.  **True Full-Stack Automation**: Running `python manage.py make:entity` generates everything from the DB model and API endpoints to the React List view and its API client.
2.  **Modular & Scalable**: Features are self-contained. Need to move an app to a microservice? It's already decoupled.
3.  **Premium Developer Experience**: Integrated i18n, standardized error handling, and a themeable component system out of the box.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd praetor-api

# Setup Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Setup Frontend
cd web
npm install
```

### 2. Initialize Database

```bash
python manage.py db:migrate
python manage.py auth:createsuperuser
python manage.py auth:makepermissions
```

### 3. Generate a Feature

```bash
# Generate a new app and entity
python manage.py make:app store
python manage.py make:entity product --app store
```

### 4. Run Everything

Running with Docker (Recommended):
```bash
docker-compose up --build
```
*API available at `http://localhost:8000`, Frontend at `http://localhost:5173`.*

## 📂 Project Structure

```
praetor-api/
├── apps/                # Backend Modular Apps (Domain-Driven)
├── core/                # CLI, Base Classes, Templates, Celery
├── config/              # Centralized configuration (FastAPI, Logging)
├── web/                 # React Frontend
│   ├── src/features/    # Frontend Modules (DDD)
│   ├── src/components/  # UI Library (shadcn/ui patterns)
│   └── src/lib/         # i18n, API client, Utils
├── manage.py            # The Heart of the DX
└── docker-compose.yml   # Full-stack orchestration
```

---
*PraetorAPI - Building scalable systems, faster.*
